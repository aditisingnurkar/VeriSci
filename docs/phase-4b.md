# Phase 4b: System Fix Pass & PubMed Evidence Coverage

## Fix Pass (Part A)
- **Retrieval Engine**: Rebuilt the TF-IDF and cosine similarity index using the genuine SciFact corpus (5,183 documents) instead of the mock 14-passage generator. Deleted `download_data.py`.
- **Classification Enhancements**: The classical Linear SVM pipeline was retrained with hard-negative mining (retrieving tricky neutral passages directly from the real corpus to prevent false positives) and enhanced TF-IDF/overlap heuristics. This significantly boosted macro-F1 over the baseline. We compared it against a zero-shot Transformer NLI model, which underperformed, so the baseline was selected.
- **Aggregation Logic**: The entire `aggregation.py` was rewritten to group evidence at the document level (preventing repeated passages from the same paper from inflating confidence). It now outputs discrete text verdicts (`SUPPORTED`, `CONTRADICTED`, `MIXED`, `INSUFFICIENT`).
- **API (FastAPI)**: Added a TTL cache (1 hour) using `uuid` keys (`verification_id`) to store the verification context securely on the server. Replaced deprecated `@app.on_event("startup")` with `lifespan` context manager.
- **Frontend Refactor**: The UI was massively updated. `mockData.js` and unused stylesheets were wiped. The verdict is now shown in a prominent, color-coded Hero block. `EvidenceCard.jsx` links to the exact passages using anchor tags, and `Analysis.jsx` properly handles genuine server loading delays instead of fake timeouts.

## PubMed Evidence Integration (Part B)
- **Live Search**: Implemented a new module `backend/retrieval/pubmed.py` to seamlessly query the live NCBI PubMed API (using `esearch` and `efetch`) via the `ENABLE_PUBMED=true` environment flag.
- **Scope Handling**: In order to prevent the system from hallucinating evidence for absurd claims, we implemented an `OUT_OF_SCOPE` reason code. If a claim lacks common biomedical keywords and neither SciFact nor PubMed return meaningful hits, the system immediately returns an `INSUFFICIENT` verdict accompanied by a clear "looks outside that scope" message.
- **Unified Pipeline**: PubMed abstracts are dynamically processed (sentence-split) and injected directly into the same sentence-level ranking and classification pipeline as SciFact, completely standardizing the output structure.

## Metrics
- **End-to-End Evaluation**: Tested on `claims_dev.jsonl` yielding a Macro-F1 of **0.31** across the full pipeline.
- **Sanity Checks**: Evaluated deterministic sanity claims ("Vaccines cause infertility", "The moon is made of cheese"). The moon query gracefully hits the out-of-scope boundary.
