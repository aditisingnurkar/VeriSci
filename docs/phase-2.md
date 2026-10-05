# Phase 2: Scientific Evidence Retrieval

## Objective
Implement an evidence retrieval module capable of matching a user's scientific claim against a scientific corpus to retrieve the most relevant evidence passages. This module answers the question: "Which scientific evidence is relevant to this claim?" using a standard Vector Space Model approach (TF-IDF with Cosine Similarity).

## SciFact Structure Used
The retrieval module relies on the official SciFact corpus structure. The expected `corpus.jsonl` schema is:
```json
{
  "doc_id": 1,
  "title": "String",
  "abstract": ["Sentence 1", "Sentence 2", "..."],
  "structured": false
}
```
Each sentence inside the `abstract` list is extracted, indexed, and treated as a discrete retrieval passage, since the ultimate ML classifier operates on sentence-level evidence.

## Dataset Preparation
To ensure reproducibility in all network environments (especially if downloading directly from AWS S3 or HuggingFace API fails), a robust reproducible dataset generation script (`backend/download_data.py`) was created. It creates a localized `.jsonl` corpus using the exact, strict SciFact schema, mimicking real domain papers (e.g. vaccines, climate change). 

## Preprocessing
`backend/retrieval/preprocess.py` parses the JSONL file and flattens the abstract arrays into individual documents. It assigns a unique ID to each sentence (e.g., `docId_sentenceIdx`) while retaining metadata (`title`, `doc_id`).

## TF-IDF Implementation & Indexing Strategy
Instead of fitting the vectorizer on-the-fly per request, the TF-IDF vectorizer and tf-idf matrix are built **offline** and saved to disk.
1. `backend/retrieval/index.py` executes the offline generation.
2. It uses `sklearn.feature_extraction.text.TfidfVectorizer` (with english stop words and `min_df=1`).
3. The resulting model, document-term matrix, and passage metadata list are serialized using `pickle` into a `saved_index/` directory.

## Similarity Calculation
`backend/retrieval/retrieve.py` loads the pre-built index into memory globally (so it only loads once per server lifecycle). Upon receiving a claim, it:
1. Transforms the claim string using the loaded TF-IDF vectorizer.
2. Computes the cosine similarity between the claim vector and all corpus document vectors.
3. Ranks the similarities and extracts the `top_k` results, ensuring their score is > 0.0.

## API Endpoint
A minimal FastAPI backend was created (`backend/main.py`) to expose this retrieval functionality.

**Endpoint:** `POST /api/retrieve`

**Request Body:**
```json
{
  "claim": "Vaccines cause infertility.",
  "top_k": 5
}
```

**Response Body:**
```json
{
  "evidence": [
    {
      "document_id": "1",
      "title": "Systematic review of COVID-19 vaccination and fertility",
      "evidence_text": "There have been concerns about the effect of COVID-19 vaccines on fertility.",
      "relevance_score": 0.23,
      "source": "SciFact"
    }
  ]
}
```

## Files Created
- `backend/download_data.py`: Creates reproducible schema-strict mock SciFact data.
- `backend/retrieval/preprocess.py`: Extracts and formats abstracts.
- `backend/retrieval/index.py`: Generates the TF-IDF models offline.
- `backend/retrieval/retrieve.py`: Core inference script for similarity matching.
- `backend/main.py`: The FastAPI server.
- `backend/run.py`: Script to start the uvicorn server.
- `docs/phase-2.md`: This documentation file.

## Files Modified
- `frontend/src/pages/Analysis.jsx`: Connected to the `POST /api/retrieve` endpoint.
- `frontend/src/pages/Results.jsx`: Updated to gracefully accept actual backend data and indicate that ML predictions are "PENDING".

## Dependencies
- `fastapi`, `uvicorn`, `scikit-learn`, `pandas`, `numpy`, `requests`

## Testing Performed
1. Tested TF-IDF offline index creation locally to ensure `saved_index/` populates correctly.
2. Tested the FastAPI startup event to ensure `load_index()` executes without errors.
3. Tested sending claims via the frontend UI. The loading screen correctly reaches out to port 8000, receives matching evidence based on vocabulary overlap, and formats it in the results interface.

## Limitations
- TF-IDF relies on exact keyword matching. It struggles with synonyms (e.g. "shot" vs "vaccine"). A denser retrieval method (like Sentence Transformers) could be a future enhancement.
- TF-IDF similarity does not imply the evidence supports the claim; it merely confirms topical relevance.

## Why Retrieval Does Not Classify Evidence
Retrieval's sole objective is finding information sharing a semantic or lexical space with the query. E.g., "Vaccines cause infertility" and "Vaccines do not cause infertility" have near-identical TF-IDF vectors. Retrieval locates the paper; it does not "read" or "understand" the relational sentiment.

## How Phase 3 Will Consume Retrieval Output
In Phase 3, the ML classifier will take the `evidence_text` output from this module alongside the original user `claim`. It will predict the relational label (SUPPORT, CONTRADICT, NEUTRAL) which will replace the current "PENDING" placeholders in the frontend UI.
