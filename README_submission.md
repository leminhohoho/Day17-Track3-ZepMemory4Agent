# Lab 17 — Multi-Memory Agent with Zep

**Nguyen Le Minh — 2A202601045**

Practice set: **11/11 PASS (100% hit rate)**, avg latency 672 ms.
No-memory baseline: **2/11 (18.2%)**. See `reports/comparison.md`.

## Three required questions

**1. Most important layer in this test set — long-term.** It decides E02, E03,
E08, E09 outright (20 of 56 auto points) and supplies half of mixed E07. It is
also the only layer needing two calls: the Context Block summarises, but the
open-loop deadline in E03 (`benchmark report`, `16:00`) only appears reliably
in the `scope="edges"` fact search, so I append edges with `limit=20`.

**2. Zep Context Block vs self-built Redis + Qdrant.** Zep gives cross-session
summarisation, entity/fact extraction with `valid_at`/`invalid_at`, and
user-scoped isolation for free — E08's recency flip and E09's isolation work
without my writing conflict-resolution logic. The costs are latency (~1.2 s per
long-term case, five sequential API calls) and loss of control: relevance
selection is opaque and I cannot tune it. Redis + Qdrant are far faster
(sub-ms KV, local ANN) and fully inspectable, but summarisation, fact validity
and forgetting all become my code.

**3. Guardrail against memory poisoning.** Never let retrieved memory act as
instructions. `src/heartbeat.py` encodes this: it may compact, de-duplicate and
expire notes, but "never create a high-impact task or preference change without
policy/human review". `MEMORY_SCHEMA.md` reinforces it — every durable record
carries `source`, `timestamp`, `confidence` and `validity`, so an injected
claim stays attributable and revocable instead of silently becoming fact.

## Benchmark analysis

1. **Lowest hit rate:** none — all four layers reach 100%. The most fragile was
   semantic: with `scope="auto"` E06/E11 failed because fact extraction drops
   literal markers (`PAYMENT-RULE-3`); `scope="episodes"` keeps raw text.
2. **Most tokens retrieved:** E02, 1400 tokens (E03 1380, E08 1375) — the whole
   user summary plus 20 fact edges.
3. **E07 (mixed)** needs long-term + semantic: `Python` (personal preference)
   and `Idempotency-Key` (shared KB). Budget trimmed long-term 1395→324 tokens.
4. **Token reduction:** 14.2% memory vs 81.8% no-memory. No-memory "wins"
   because it retrieves nothing — reduction is only meaningful beside hit rate.

## E08 recency and E10 compaction

E08: newer BLUEBIRD-42/TypeScript facts supersede the older Python preference;
the old fact stays for provenance, invalidated rather than deleted. E10:
sliding-window compaction promotes `REVIEW-DEADLINE-1600` to a durable note, so
`Friday`/`16:00` survive after the raw turn is evicted — buffer alone would
have kept it only until the window filled.
