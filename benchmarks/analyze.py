"""Agrège runs.json → summary.json + summary.csv (moyennes, IC bootstrap 95 %, comparaisons appariées).

    venv/bin/python -m bench.analyze [--results bench/results]
"""
from __future__ import annotations

import argparse
import csv
import json
import os

from bench.dataset import load
from bench.metrics import (bootstrap_ci, complete_at_k, ndcg_at_k, paired_bootstrap_diff, percentile,
                           recall_at_k, reciprocal_rank, stale_first, up_to_date_at_k)

HERE = os.path.dirname(os.path.abspath(__file__))
RANKERS = ["pryzm_actuel", "pryzm_hybride", "pryzm_sans_rerank", "pryzm_passage", "bm25", "dense_e5"]


def per_query(run: dict, q: dict) -> dict:
    """Valeurs par question (0/1 ou réel) pour un système classant."""
    r, rel, stale = run["ranked"], q["relevant"], q["stale"]
    # Abstention = liste vide OU signal explicite « aucun résultat fiable » (v3, additif).
    abst = (not r) or bool(run.get("no_reliable_result"))
    if q["kind"] == "unanswerable":
        return {"abstention_ok": 1.0 if abst else 0.0}
    out = {"r@1": recall_at_k(r, rel, 1), "r@5": recall_at_k(r, rel, 5), "mrr": reciprocal_rank(r, rel),
           "ndcg@10": ndcg_at_k(r, rel, 10), "complet@5": complete_at_k(r, rel, 5),
           "abstention_a_tort": 1.0 if abst else 0.0}
    if q["kind"] == "temporal":
        out["a_jour@5"] = up_to_date_at_k(r, rel, stale, 5)
        out["perime_en_tete"] = stale_first(r, rel, stale)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(HERE, "results"))
    a = ap.parse_args()
    data = json.load(open(os.path.join(a.results, "runs.json"), encoding="utf-8"))
    version = data["meta"]["dataset"].split("_")[-1].split(".")[0]
    qs = {q["id"]: q for q in load(version)["queries"]}
    sizes = data["meta"]["scales"]

    vals: dict[tuple, dict[str, list[float]]] = {}   # (size, system, groupe) -> métrique -> valeurs (ordre qid)
    lat: dict[tuple, list[float]] = {}
    for run in sorted(data["runs"], key=lambda x: x["qid"]):
        q = qs[run["qid"]]
        groups = ["toutes_avec_reponse" if q["kind"] != "unanswerable" else "sans_reponse", q["kind"]]
        if q["kind"] == "simple":
            groups.append("style_" + q["style"])
        if run["system"].startswith("contexte_"):
            if q["kind"] == "unanswerable":
                continue
            v = {"present_dans_contexte": 1.0 if set(q["relevant"]) <= set(run["in_context"]) else 0.0}
        else:
            v = per_query(run, q)
            lat.setdefault((run["size"], run["system"]), []).append(run["ms"])
        for g in groups:
            d = vals.setdefault((run["size"], run["system"], g), {})
            for k, x in v.items():
                d.setdefault(k, []).append(x)

    rows = []
    for (size, system, g), d in sorted(vals.items()):
        for k, xs in d.items():
            m, lo, hi = bootstrap_ci(xs)
            rows.append({"size": size, "system": system, "group": g, "metric": k, "n": len(xs),
                         "mean": round(m, 4), "ci_low": round(lo, 4), "ci_high": round(hi, 4)})
    latency = [{"size": s, "system": sy, "n": len(x), "p50_ms": round(percentile(x, 50), 1),
                "p95_ms": round(percentile(x, 95), 1)} for (s, sy), x in sorted(lat.items())]

    comps = []
    for size in sizes:
        for g, metric in (("toutes_avec_reponse", "mrr"), ("toutes_avec_reponse", "r@5"), ("toutes_avec_reponse", "r@1"),
                          ("simple", "mrr"), ("multihop", "complet@5"), ("temporal", "a_jour@5"),
                          ("style_indirecte", "r@5"), ("style_crosslingue", "r@5"), ("style_identifiant", "r@5"),
                          ("sans_reponse", "abstention_ok")):
          for a_sys in ("pryzm_actuel", "pryzm_hybride"):
            base = vals.get((size, a_sys, g), {}).get(metric)
            for other in RANKERS:
                o = vals.get((size, other, g), {}).get(metric)
                if base and o and other != a_sys:
                    comps.append({"size": size, "group": g, "metric": metric, "a": a_sys, "b": other,
                                  **{k: (round(v, 4) if isinstance(v, float) else v)
                                     for k, v in paired_bootstrap_diff(base, o).items()}})

    out = {"meta": data["meta"], "metrics": rows, "latency": latency, "paired": comps}
    json.dump(out, open(os.path.join(a.results, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(os.path.join(a.results, "summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(a.results, "paired.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(comps[0]))
        w.writeheader()
        w.writerows(comps)
    print(f"{len(rows)} lignes de métriques, {len(comps)} comparaisons appariées → {a.results}")


if __name__ == "__main__":
    main()
