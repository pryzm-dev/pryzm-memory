"""Métriques de recherche + intervalles de confiance par bootstrap (pur Python)."""
from __future__ import annotations

import math
import random


def recall_at_k(ranked: list[str], relevant: list[str], k: int) -> float:
    """Part des souvenirs pertinents présents dans les k premiers résultats."""
    if not relevant:
        return 0.0
    top = set(ranked[:k])
    return sum(1 for r in relevant if r in top) / len(relevant)


def complete_at_k(ranked: list[str], relevant: list[str], k: int) -> float:
    """1 si TOUS les souvenirs pertinents sont dans les k premiers (multi-sauts)."""
    return 1.0 if relevant and set(relevant) <= set(ranked[:k]) else 0.0


def reciprocal_rank(ranked: list[str], relevant: list[str]) -> float:
    rel = set(relevant)
    for i, mid in enumerate(ranked, start=1):
        if mid in rel:
            return 1.0 / i
    return 0.0


def ndcg_at_k(ranked: list[str], relevant: list[str], k: int = 10) -> float:
    rel = set(relevant)
    dcg = sum(1.0 / math.log2(i + 2) for i, mid in enumerate(ranked[:k]) if mid in rel)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(min(len(rel), k)))
    return dcg / idcg if idcg else 0.0


def up_to_date_at_k(ranked: list[str], relevant: list[str], stale: list[str], k: int = 5) -> float:
    """Mise à jour : 1 si le fait récent est dans le top k ET classé avant le fait périmé."""
    if not relevant:
        return 0.0
    new = relevant[0]
    if new not in ranked[:k]:
        return 0.0
    pos_new = ranked.index(new)
    for s in stale:
        if s in ranked and ranked.index(s) < pos_new:
            return 0.0
    return 1.0


def stale_first(ranked: list[str], relevant: list[str], stale: list[str]) -> float:
    """1 si le fait PÉRIMÉ sort avant le fait à jour (erreur la plus gênante)."""
    if not stale or not ranked:
        return 0.0
    pos = {mid: i for i, mid in enumerate(ranked)}
    ps = min((pos[s] for s in stale if s in pos), default=None)
    if ps is None:
        return 0.0
    pn = pos.get(relevant[0]) if relevant else None
    return 1.0 if pn is None or ps < pn else 0.0


def percentile(xs: list[float], p: float) -> float:
    if not xs:
        return float("nan")
    s = sorted(xs)
    idx = (len(s) - 1) * p / 100.0
    lo, hi = math.floor(idx), math.ceil(idx)
    return s[lo] if lo == hi else s[lo] + (s[hi] - s[lo]) * (idx - lo)


def bootstrap_ci(values: list[float], n_boot: int = 2000, alpha: float = 0.05, seed: int = 7) -> tuple[float, float, float]:
    """Moyenne + IC percentile (1-alpha) par rééchantillonnage des questions."""
    if not values:
        return (float("nan"),) * 3
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(n_boot):
        means.append(sum(values[rng.randrange(n)] for _ in range(n)) / n)
    return (sum(values) / n, percentile(means, 100 * alpha / 2), percentile(means, 100 * (1 - alpha / 2)))


def paired_bootstrap_diff(a: list[float], b: list[float], n_boot: int = 2000, alpha: float = 0.05,
                          seed: int = 11) -> dict:
    """Différence moyenne a-b sur les MÊMES questions + IC + p bilatéral approché."""
    if len(a) != len(b) or not a:
        raise ValueError("listes appariées de même longueur requises")
    d = [x - y for x, y in zip(a, b)]
    mean, lo, hi = bootstrap_ci(d, n_boot, alpha, seed)
    rng = random.Random(seed + 1)
    n = len(d)
    le0 = ge0 = 0
    for _ in range(n_boot):
        m = sum(d[rng.randrange(n)] for _ in range(n)) / n
        le0 += m <= 0
        ge0 += m >= 0
    p = min(1.0, 2 * min(le0, ge0) / n_boot)
    return {"diff": mean, "ci_low": lo, "ci_high": hi, "p_boot": p, "n": n}
