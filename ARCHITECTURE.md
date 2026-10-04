# How Pryzm works

A high-level map. Each section says what is public and what is not.

## 1. Interface

Pryzm speaks **MCP** (Model Context Protocol) over HTTP, with **OAuth 2.1** for sign-in.
You add one URL to an AI assistant that supports custom connectors; the assistant then gets
tools to store, search and browse your memories (store, search, get, timeline, project context,
what's-up overview, preference passport, and a small planning layer).
Anything that speaks MCP can use it. The memory is not tied to one model provider.

## 2. Storage and isolation

- PostgreSQL with `pgvector` (HNSW index).
- **One schema and one database role per user.** Isolation is physical, not a row filter:
  a query running as one user's role cannot see another user's tables, and fails closed.
- Optional sealed mode: the content of a memory is encrypted with a key only the user can
  unlock (see §4).

## 3. Retrieval

A question goes through four stages:

1. **Dense search**: multilingual embeddings (`e5-small`), cosine distance, so a question in
   French can find a memory written in English.
2. **Lexical search**: a BM25-style arm, so rare names and identifiers are not lost by embeddings.
3. **Fusion**: Reciprocal Rank Fusion of the two lists (k = 60):
   `score(d) = Σ 1 / (k + rank_i(d))`.
4. **Rerank**: a multilingual cross-encoder re-scores the shortlist, then a recency and
   importance weighting breaks ties between old and new versions of the same fact.

Engine v3 (see the changelog) adds a graded confidence level per result so the assistant can
hedge instead of asserting. A memory graph links related memories and can pull neighbours into the answer.

Public: the pipeline above, and measured results ([`benchmarks/`](benchmarks)).
Private: the implementation, thresholds, weights and prompts.

## 4. The vault (published: [`vault/`](vault))

- **AES-256-GCM** per value. The associated data binds each ciphertext to its user, table,
  row and column, so a value copied elsewhere does not decrypt.
- Keys: a random data key is wrapped by a key derived from the user's secret with **Argon2id**
  (t = 3, 64 MiB, 1 lane). Session tokens use **HKDF-SHA256**.
- **Blind index**: an HMAC lets the server match exact values without storing them in clear.
- Error messages never contain content or secrets.

Plain-language promise: your memories are yours, encrypted at rest and hosted in the EU.

## 5. What we do not publish, and why

Engine tuning, prompts, provisioning, billing, administration and the application code are
private. We publish what lets you judge the quality and the security of the system.
