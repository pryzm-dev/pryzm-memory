# LoCoMo: retrieval results

[LoCoMo](https://github.com/snap-research/locomo) is a public benchmark of 10 long conversations
between two people, with questions whose answers are spread across the dialogue. Each question lists
the dialogue turns that hold the evidence.

**What we measured:** every turn becomes a dated memory (5,882 memories); for each question we check
whether the evidence turns come back in Pryzm's results. Categories 1–4 (1,532 questions); category 5
(adversarial) is excluded, as is usual for this dataset. Production engine settings, run on
4 October 2026, no LLM anywhere.

**What we did not measure:** the final answer. Other systems publish a "J" score where an LLM writes an
answer and another LLM grades it. That is a different number: **these results cannot be compared with
it.**

| Evidence in the top 5 (recall@5) | Pryzm | Keywords only (BM25) | Meaning only (e5-small) |
|---|---|---|---|
| All questions (n = 1,532) | **0.636** (0.614–0.657) | 0.521 (0.499–0.546) | 0.365 (0.343–0.387) |
| Single-hop (n = 841) | **0.724** (0.694–0.754) | 0.630 | 0.425 |
| Temporal (n = 321) | **0.718** (0.670–0.765) | 0.622 | 0.451 |
| Multi-hop (n = 281) | **0.372** (0.331–0.412) | 0.175 | 0.156 |
| Open-domain (n = 89) | **0.332** (0.244–0.416) | 0.226 | 0.150 |
| MRR, all questions | **0.601** (0.579–0.623) | 0.430 | 0.277 |

95 % bootstrap confidence intervals in brackets.

**Reading:** Pryzm scores above both baselines in every category; the gap is clear everywhere except
open-domain, where the sample is small (89 questions) and the intervals overlap. Multi-hop
(evidence spread over several turns) and open-domain questions remain weak: that is where we work next.

Files: `summary.json` (all metrics), `runs.json` (ranked results per question, memory IDs only; the
dataset itself is not redistributed), `locomo.py` (the harness; it calls our private engine).
