# Live demo guide

Start the real local product with the repository virtual environment and the
Phase 2 demo runner. It opens on localhost port 8765.

The first start loads the already cached pinned MiniLM model. It does not need
network access. The page searches the frozen Phase 2 corpus and uses the Phase
2 exploratory configuration: match weight 0 and conflict weight .003.

For a short professor showcase:

1. Start with the default CVE-2023-46747 question.
2. Point out the same query in the four side-by-side rankings.
3. In the identifier-aware card, explain the match/conflict decision and rank
   movement relative to RRF.
4. Open an official source link from a result to demonstrate provenance.
5. Close with the visible limitation banner: this is an author-annotated,
   CVE-only exploratory evaluation, not an independently validated benchmark.

The demo is intentionally local-first. It runs the actual TF-IDF, MiniLM, RRF,
and reranking implementations, rather than replaying saved rankings or using a
mock model.
