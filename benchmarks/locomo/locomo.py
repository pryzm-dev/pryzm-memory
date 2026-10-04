"""Banc public LoCoMo (snap-research/locomo, 10 conversations, 1 986 questions) : partie
« retrouver » uniquement. Chaque réplique devient un souvenir daté ; on mesure si les répliques
citées en preuve par le jeu sortent dans les k premiers résultats. Aucun LLM n'intervient :
ce n'est PAS le score « J » (réponse notée par un LLM) que publient d'autres systèmes.

    set -a; . ~/sauvegardes/pryzm-test-local.env; set +a
    venv/bin/python -m bench.locomo --data ~/bancs/locomo/locomo10.json --out bench/results_locomo
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone

from bench.metrics import bootstrap_ci, recall_at_k, reciprocal_rank
from bench.run import BM25, LIMIT, V3_FLAGS, _setup_env, encode, git_rev, ingest, pryzm_search

CATEGORIES = {1: "multi_sauts", 2: "temporel", 3: "domaine_ouvert", 4: "simple"}  # 5 = adversarial, exclu (convention LoCoMo)
_DATE = re.compile(r"(\d{1,2}):(\d{2})\s*(am|pm) on (\d{1,2}) (\w+),? (\d{4})", re.I)


def parse_date(s: str) -> datetime:
    h, mi, ap, d, mo, y = _DATE.search(s).groups()
    h = int(h) % 12 + (12 if ap.lower() == "pm" else 0)
    return datetime.strptime(f"{d} {mo} {y} {h}:{mi}", "%d %B %Y %H:%M").replace(tzinfo=timezone.utc)


def memory_id(conv: int, dia_id: str) -> str:
    return f"c{conv}-" + dia_id.replace(":", "-")


def corpus_for(conv: int, sample: dict, now: datetime) -> list[dict]:
    c, out = sample["conversation"], []
    n = 1
    while f"session_{n}" in c:
        when = parse_date(c[f"session_{n}_date_time"])
        for t in c[f"session_{n}"]:
            text = f"[{when:%d %B %Y}] {t['speaker']}: {t['text']}"
            if t.get("blip_caption"):
                text += f" (partage une photo : {t['blip_caption']})"
            out.append({"id": memory_id(conv, t["dia_id"]), "text": text, "type": "note",
                        "importance": 0.5, "age_days": max(0, (now - when).days)})
        n += 1
    return out


def questions_for(conv: int, sample: dict) -> list[dict]:
    qs = []
    for i, q in enumerate(sample["qa"]):
        if q.get("category") not in CATEGORIES or not q.get("evidence"):
            continue
        ev = [memory_id(conv, e.strip()) for e in q["evidence"] if re.fullmatch(r"D\d+:\d+", e.strip())]
        if ev:
            qs.append({"qid": f"c{conv}-q{i}", "text": q["question"], "cat": CATEGORIES[q["category"]], "relevant": ev})
    return qs


def summarize(rows: list[dict]) -> dict:
    out = {}
    for system in sorted({r["system"] for r in rows}):
        rs = [r for r in rows if r["system"] == system]
        for group in ["toutes", *CATEGORIES.values()]:
            g = rs if group == "toutes" else [r for r in rs if r["cat"] == group]
            if not g:
                continue
            for m in ("r@5", "r@10", "mrr"):
                mean, lo, hi = bootstrap_ci([r[m] for r in g])
                out[f"{system}/{group}/{m}"] = {"n": len(g), "moyenne": round(mean, 3), "ic95": [round(lo, 3), round(hi, 3)]}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "results_locomo"))
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--convs", type=int, default=0, help="0 = les 10 conversations")
    a = ap.parse_args()
    _setup_env()
    os.environ.update(V3_FLAGS)
    os.environ.pop("ABSTAIN_MAX_SIMILARITY", None)  # coupé en prod
    import numpy as np
    import db_pg

    data = json.load(open(os.path.expanduser(a.data)))
    if a.convs:
        data = data[:a.convs]
    now = datetime.now(timezone.utc)
    rows: list[dict] = []
    for conv, sample in enumerate(data):
        corpus, qs = corpus_for(conv, sample, now), questions_for(conv, sample)
        tenant = f"bench_locomo_{conv}"
        vec = dict(zip([m["id"] for m in corpus], encode([m["text"] for m in corpus], "query: ")))
        ingest(tenant, corpus, vec)
        bm25 = BM25([(m["id"], m["text"]) for m in corpus])
        ids = list(vec)
        mat = np.array([vec[i] for i in ids], dtype=np.float32)
        qv = encode([q["text"] for q in qs], "query: ")
        for q, v in zip(qs, qv):
            dense = [ids[j] for j in np.argsort(-(mat @ np.array(v, dtype=np.float32)))[:LIMIT]]
            systems = {"pryzm": pryzm_search(tenant, q["text"], "pryzm_actuel")[0],
                       "bm25": [i for i, _ in bm25.search(q["text"], LIMIT)],
                       "dense_e5": dense}
            for name, ranked in systems.items():
                rows.append({"system": name, "qid": q["qid"], "cat": q["cat"], "ranked": ranked,
                             "relevant": q["relevant"], "r@5": recall_at_k(ranked, q["relevant"], 5),
                             "r@10": recall_at_k(ranked, q["relevant"], 10),
                             "mrr": reciprocal_rank(ranked, q["relevant"])})
        print(f"conversation {conv}: {len(corpus)} souvenirs, {len(qs)} questions", flush=True)
        if not a.keep:
            db_pg.purge_tenant(tenant)

    os.makedirs(a.out, exist_ok=True)
    meta = {"dataset": "LoCoMo locomo10.json (snap-research/locomo)", "commit": git_rev(),
            "categories": "1-4 (5 adversarial exclue)", "limit": LIMIT, "engine": "réglages de prod",
            "mesure": "rappel des répliques citées en preuve ; aucun LLM"}
    json.dump({"meta": meta, "runs": rows}, open(os.path.join(a.out, "runs.json"), "w"), ensure_ascii=False)
    summary = summarize(rows)
    json.dump({"meta": meta, "summary": summary}, open(os.path.join(a.out, "summary.json"), "w"),
              ensure_ascii=False, indent=1)
    for k, v in summary.items():
        print(f"{k:38} {v['moyenne']:.3f} [{v['ic95'][0]:.3f}–{v['ic95'][1]:.3f}] n={v['n']}")


if __name__ == "__main__":
    main()
