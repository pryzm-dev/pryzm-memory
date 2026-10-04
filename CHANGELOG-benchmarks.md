# Search engine: what we measured, kept and dropped

Method: tune on one synthetic dataset (v1), validate once on a second dataset generated
beforehand with different templates (v2, "held-out"). Every change is compared with the original
run on the same questions, with 95 % bootstrap confidence intervals. We keep a change only if it
helps without degrading another category beyond noise.

## Engine v3 (validated on held-out data, released 3 October 2026)

| Held-out measure (2,000 memories) | Before | After | Difference (95 % CI) |
|---|---|---|---|
| Right memory first | 0.465 | 0.529 | +0.064 (+0.01 to +0.12) |
| Right memory in top 5 | 0.571 | 0.651 | +0.080 (+0.03 to +0.13) |
| MRR | 0.553 | 0.618 | +0.064 (+0.02 to +0.11) |
| Updated fact returned and ranked above the old one | 0.417 | 0.708 | +0.292 (+0.12 to +0.46) |
| Questions needing two memories, both in top 5 | 0.208 | 0.417 | +0.208 (0 to +0.42, p = 0.06) |

Versus semantic-only search with the same model: MRR +0.162 (+0.10 to +0.22) on the held-out set.

What helped: repairing the keyword arm of the hybrid search, a freshness term applied after the
reranker so a newer version of a fact beats an older one, and a second "bridge" pass that finds a
second memory sharing a rare name with the first.

## What did not work, and what we did not ship

- **A binary "nothing reliable found" signal.** It looked good on the tuning set and did not hold
  on held-out data (28 % false alarms versus 14 %). It stays off. We replaced the idea with a graded
  confidence per result, whose calibration did hold on both datasets.
- **Cross-language gain.** A +0.089 gain seen on the tuning set did not reproduce on held-out data.
  It probably came from the dataset.
- **Quantizing the reranker for speed.** It changed the ranking too much (rank correlation 0.83) and
  was dropped. Capping candidates sent to the reranker lowered quality and was dropped too.
- **Latency target missed.** The 95th percentile is 550 to 835 ms depending on the run; the
  cross-encoder dominates. A smaller reranker is future work.

## Reranker latency (4 October 2026)

In production, memories are much longer than in the benchmark (median 72 characters there). The
cross-encoder read up to 115 candidates of up to 512 tokens each, and a search could take 4 to 6 s.
It now reads at most 40 candidates (the benchmark never sends more) and the first 128 tokens of each
(no benchmark memory reaches that length). Benchmark results are identical to the third decimal;
worst case measured on our server for long memories: 14.5 s before, about 1.3 s after.
Trade-off, stated plainly: for a very long memory the reranker judges its beginning only; the
semantic and keyword stages still read the full text.

Raw results for the original run are in [`benchmarks/results`](benchmarks/results).
