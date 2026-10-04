# Pryzm Memory

**Your memory. All your AIs.**

Pryzm is a persistent memory layer that lives beside your AI assistants, not inside them.
Tell one assistant something worth keeping; any other assistant you connect can recall it later.
One source of truth for your context, and it belongs to you.

→ Product: https://pryzm-memory.com

In development since June 2026.

## What this repository is

Pryzm is a hosted service, and its engine is **not** open source. This repository is the part
we choose to put in the open so that you can check our claims instead of trusting them:

| Folder | What you can verify |
|---|---|
| [`benchmarks/`](benchmarks) | The retrieval benchmark: protocol, synthetic datasets, metrics, raw results, and a report that states where Pryzm loses as clearly as where it wins. |
| [`vault/`](vault) | The cryptographic core of the per-user vault: AES-256-GCM with bound context, Argon2id, HKDF, key wrapping, blind index. Real production code. |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | How a memory is stored, found and protected, and what is deliberately not published. |
| [`CHANGELOG-benchmarks.md`](CHANGELOG-benchmarks.md) | What we changed in the search engine, what worked, what we dropped, with numbers. |

## Headline numbers

Measured on a synthetic dataset of 2,000 memories and 223 questions, no real user data
(full report: [`benchmarks/rapport.md`](benchmarks/rapport.md), in French).

- Original run (2 October 2026, engine before v3): the right memory is **first in 53 %** of cases
  (95 % CI 47–60 %) and **in the top 5 in 70 %** (63–76 %).
- Engine in production since 3 October (v3), same dataset: **first in 61 %** (54–68 %), **top 5 in 77 %**
  (71–83 %); raw file [`benchmarks/results_v3/v1_production.json`](benchmarks/results_v3/v1_production.json).
- It beats keyword-only search (BM25) by +0.165 MRR (CI +0.089 to +0.237), mostly when the question
  is asked in another language than the memory.
- It does **not** measurably beat semantic-only search with the same embedding model
  (+0.022 MRR, CI −0.035 to +0.075): we say so.
- Against a naive "paste the most recent notes into the prompt" baseline (20,000 characters),
  Pryzm returns every useful memory in its top 5 for 64 % of questions versus 26 %.
- Known weaknesses, measured and published: superseded facts (the old version ranks first 71 % of
  the time on the original run), questions needing two memories, and questions with no answer.

Benchmarks are re-run and published here as the engine changes.

## What is not here

The retrieval engine and its tuning, prompts, multi-tenant provisioning, billing, the web
application and operations tooling stay private. Publishing them would help attackers more than
it would help users.

## License

MIT for the code in this repository. See [`LICENSE`](LICENSE).
