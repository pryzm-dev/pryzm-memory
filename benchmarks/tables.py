"""Imprime les tableaux Markdown du rapport à partir de summary.json / runs.json.

    venv/bin/python -m bench.tables [--results bench/results] > /tmp/tables.md
"""
from __future__ import annotations

import argparse
import json
import os

from bench.dataset import load

HERE = os.path.dirname(os.path.abspath(__file__))
SYSTEMS = ["pryzm_actuel", "pryzm_hybride", "pryzm_passage", "pryzm_sans_rerank", "dense_e5", "bm25"]


def fmt(r: dict | None) -> str:
    return "n/d" if not r else f"{r['mean']:.3f} [{r['ci_low']:.3f}–{r['ci_high']:.3f}]"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(HERE, "results"))
    a = ap.parse_args()
    s = json.load(open(os.path.join(a.results, "summary.json"), encoding="utf-8"))
    idx = {(r["size"], r["system"], r["group"], r["metric"]): r for r in s["metrics"]}
    sizes = s["meta"]["scales"]
    big = max(sizes)

    def table(title, rows, size=big):
        print(f"\n### {title} (base de {size} souvenirs)\n")
        print("| Système | " + " | ".join(h for h, _, _ in rows) + " |")
        print("|---|" + "---|" * len(rows))
        for sy in SYSTEMS:
            print(f"| {sy} | " + " | ".join(fmt(idx.get((size, sy, g, m))) for _, g, m in rows) + " |")

    table("Questions avec réponse (n=183)", [("Recall@1", "toutes_avec_reponse", "r@1"),
                                              ("Recall@5", "toutes_avec_reponse", "r@5"),
                                              ("MRR", "toutes_avec_reponse", "mrr"),
                                              ("nDCG@10", "toutes_avec_reponse", "ndcg@10")])
    table("Par type de question", [("Simples MRR (n=135)", "simple", "mrr"),
                                   ("Multi-sauts complet@5 (n=24)", "multihop", "complet@5"),
                                   ("Mises à jour à jour@5 (n=24)", "temporal", "a_jour@5"),
                                   ("Périmé en tête (n=24)", "temporal", "perime_en_tete"),
                                   ("Sans réponse : abstention (n=40)", "sans_reponse", "abstention_ok")])
    table("Par style (faits simples, Recall@5, paraphrase n=41, autre langue et indirecte n=45)",
          [("Paraphrase FR", "style_paraphrase", "r@5"), ("Interlinguistique", "style_crosslingue", "r@5"),
           ("Indirecte", "style_indirecte", "r@5"), ("Identifiant exact (n=4)", "style_identifiant", "r@5")])

    print("\n### Passage à l'échelle : MRR (questions avec réponse)\n")
    print("| Système | " + " | ".join(str(z) for z in sizes) + " |")
    print("|---|" + "---|" * len(sizes))
    for sy in SYSTEMS:
        print(f"| {sy} | " + " | ".join(fmt(idx.get((z, sy, "toutes_avec_reponse", "mrr"))) for z in sizes) + " |")

    print("\n### Approximation « mémoire en texte injectée dans le contexte » : part des questions dont TOUS les souvenirs utiles tiennent dans le texte injecté\n")
    budgets = s["meta"]["context_budgets"]
    print("| Budget (caractères) | " + " | ".join(str(z) for z in sizes) + " |")
    print("|---|" + "---|" * len(sizes))
    for b in budgets:
        print(f"| {b} | " + " | ".join(fmt(idx.get((z, f"contexte_{b}", "toutes_avec_reponse", "present_dans_contexte")))
                                    for z in sizes) + " |")

    print("\n### Latence de recherche (ms, machine de test)\n")
    print("| Système | " + " | ".join(f"{z} p50 / p95" for z in sizes) + " |")
    print("|---|" + "---|" * len(sizes))
    lat = {(r["size"], r["system"]): r for r in s["latency"]}
    for sy in SYSTEMS:
        print(f"| {sy} | " + " | ".join(
            f"{lat[(z, sy)]['p50_ms']:.0f} / {lat[(z, sy)]['p95_ms']:.0f}" if (z, sy) in lat else "n/d" for z in sizes) + " |")

    print(f"\n### Comparaisons appariées (base {big}, différence a − b, IC 95 %, p bootstrap)\n")
    print("| a | b | groupe | métrique | diff | IC 95 % | p |")
    print("|---|---|---|---|---|---|---|")
    for c in s["paired"]:
        if c["size"] == big and c["b"] in ("dense_e5", "bm25", "pryzm_actuel"):
            print(f"| {c['a']} | {c['b']} | {c['group']} | {c['metric']} | {c['diff']:+.3f} | "
                  f"[{c['ci_low']:+.3f} ; {c['ci_high']:+.3f}] | {c['p_boot']:.3f} |")

    # Courbe d'abstention : et si on refusait de répondre sous un score de reranker donné ?
    runs = json.load(open(os.path.join(a.results, "runs.json"), encoding="utf-8"))["runs"]
    qs = {q["id"]: q for q in load()["queries"]}
    rr = [r for r in runs if r["size"] == big and r["system"] == "pryzm_actuel"]
    print(f"\n### Seuil hypothétique sur le score du reranker (pryzm_actuel, base {big})\n")
    print("| Seuil | Sans réponse : abstention correcte | Avec réponse : abstention à tort | Avec réponse : Recall@1 conservé |")
    print("|---|---|---|---|")
    for thr in (-4, -2, -1, 0, 1, 2, 3, 4):
        un = [r for r in rr if qs[r["qid"]]["kind"] == "unanswerable"]
        an = [r for r in rr if qs[r["qid"]]["kind"] != "unanswerable"]
        ok = sum(1 for r in un if r["top_rerank"] is None or r["top_rerank"] < thr) / len(un)
        wrong = sum(1 for r in an if r["top_rerank"] is None or r["top_rerank"] < thr) / len(an)
        kept = sum(1 for r in an if r["top_rerank"] is not None and r["top_rerank"] >= thr
                   and r["ranked"][:1] and r["ranked"][0] in qs[r["qid"]]["relevant"]) / len(an)
        print(f"| {thr} | {ok:.2f} | {wrong:.2f} | {kept:.2f} |")


if __name__ == "__main__":
    main()
