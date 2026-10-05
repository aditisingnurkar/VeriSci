# Phase 4: Evidence Aggregation and Final Verdict

## Overview
Phase 4 connects the Information Retrieval module (Phase 2) and the Machine Learning Classifier (Phase 3) into a single, cohesive end-to-end verification pipeline. It implements an aggregation logic that synthesizes individual, sentence-level predictions into a single final verdict for the user's scientific claim.

## Complete Pipeline
The system now operates autonomously through the following sequence:

1. **User Claim**: The user submits a scientific claim via the UI.
2. **Phase 2 (Retrieval)**: The backend searches the SciFact TF-IDF index for the top-k most relevant evidence passages.
3. **Phase 3 (ML Classification)**: The Linear SVM ML classifier evaluates each retrieved passage independently against the claim, outputting a prediction (`SUPPORT`, `CONTRADICT`, `NEUTRAL`) and a calibrated confidence score.
4. **Phase 4 (Aggregation)**: The system analyzes the spread, counts, and confidences of all passage-level predictions to determine a single, overall verdict.

## API Architecture
A new, unified endpoint was exposed to represent the complete verification operation.

**Endpoint:** `POST /api/verify`

**Request:**
```json
{
  "claim": "Vitamin C cures the common cold.",
  "top_k": 5
}
```

**Response Schema:**
```json
{
  "claim": "Vitamin C cures the common cold.",
  "verdict": "LIKELY SUPPORTED",
  "confidence": 1.0,
  "evidence": [
    {
      "document_id": "4",
      "title": "Vitamin C and the common cold",
      "evidence_text": "Vitamin C has long been touted as a cure for the common cold.",
      "relevance_score": 0.67,
      "source": "SciFact",
      "prediction": "SUPPORT",
      "confidence": 0.76
    }
  ],
  "supportingCount": 1,
  "contradictingCount": 0,
  "neutralCount": 0
}
```
*Note: If no evidence is found, the system gracefully handles the empty state and returns `INCONCLUSIVE`.*

## Aggregation Logic & Verdict Rules
The core logic resides in `backend/aggregation.py`. It does not simply average the scores. Instead, it aggregates predictions structurally:

1. **Counts**: It tallies the number of `SUPPORT`, `CONTRADICT`, and `NEUTRAL` passages.
2. **Weighted Score**: It calculates the sum of ML confidences for supporting versus contradicting passages.
3. **Rules**:
   - **LIKELY SUPPORTED**: If the `support_score` is strictly greater than the `contradict_score`, and there is at least one supporting passage (and more supporting passages than contradicting ones).
   - **LIKELY CONTRADICTED**: If the `contradict_score` is strictly greater than the `support_score`, and there is at least one contradicting passage (and more contradicting passages than supporting ones).
   - **INCONCLUSIVE**: If neither condition is met (e.g., highly conflicting evidence, purely neutral evidence, or no evidence retrieved).

Confidence is formulated based on the ratio of the winning side's score to the total non-neutral score. The system is entirely transparent; individual passage predictions are retained and passed to the frontend.

## Frontend Integration
The React frontend (Phase 1 UI) was securely wired to the new `POST /api/verify` endpoint, and the presentation of results was heavily redesigned.

- **`Analysis.jsx`**: Loading states reflect the actual process without artificial waiting.
- **Results Presentation Hierarchy (`Results.jsx`)**: The UI no longer uses a generic "dashboard" layout. Instead, it employs a natural-language, document-like hierarchy:
  1. **Primary Answer**: A dynamically generated, clear natural-language conclusion (e.g., "The available scientific evidence does not support the claim that vaccines cause infertility.").
  2. **Technical Status**: Displays the raw Phase 4 verdict (e.g., `LIKELY CONTRADICTED`) and confidence percentage.
  3. **Claim context**: Reiterates the exact original claim and how many papers were analyzed.
  4. **Integrated Scientific Evidence**: `EvidenceCard` components were upgraded so the ML interpretation (`SUPPORT`, `CONTRADICT`, `NEUTRAL`) and confidence are attached *directly* to the evidence passage they were generated from.
  5. **Evidence Breakdown**: A clear tally of the counts.
  6. **Overall Assessment**: A concise explanation of how the counts resulted in the technical verdict.
- **Scientific Responsibility**: The natural-language answers are designed to communicate the strength of the evidence without overclaiming absolute scientific certainty.
- **Consistency**: All data matches the single Phase 4 API response; no mock data is used for verification elements. The RAG explanation block and chat UI remain as placeholders for Phase 5.

## Testing Performed
End-to-end tests were performed verifying that:
1. `POST /api/verify` correctly handles both valid and irrelevant claims.
2. The ML classifier predictions correctly map to the retrieved evidence arrays.
3. The React UI safely digests the structured backend response and prevents crash cascades when evidence lists are empty.

## Limitations & Handoff to Phase 5
**Limitation**: The classical ML model (Linear SVM + TF-IDF) struggles with semantic nuances such as negation. For instance, "Vitamin C does not cure..." can erroneously trigger a `SUPPORT` prediction for the claim "Vitamin C cures..." due to high lexical overlap. 
**Phase 5 Resolution**: The system provides all structural plumbing necessary for Phase 5. In Phase 5, the classical ML classifier will be replaced by (or supplemented with) an LLM using Retrieval-Augmented Generation (RAG) which will natively grasp semantic negation and generate the final human-readable rationale.
