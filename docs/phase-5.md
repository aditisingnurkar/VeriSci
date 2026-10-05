# Phase 5: RAG Explanation & Claim Chat

## Overview
Phase 5 introduces a **Retrieval-Augmented Generation (RAG)** layer strictly designed to *explain* the verification results. 
**Crucial Architecture Distinction**: The LLM does *not* participate in retrieving evidence, and it does *not* make or alter the classification verdict. The ML/Aggregation layer completely dictates the verdict. The LLM only surfaces insights from the retrieved passages in a conversational manner.

## Implementation Details
- **Context Construction**: A dedicated endpoint `/api/verify` produces a verification object, which is cached via an in-memory TTL store (1 hour lifetime) using a generated UUID (`verification_id`).
- **Explanation Module**: When the UI mounts, `/api/explain` is called with the `verification_id`. The server rebuilds a grounding context comprising the system's verdict and the top 10 most relevant evidence passages. The LLM then generates a 4-6 sentence plain language explanation of *why* the ML classification occurred.
- **Chat Interface**: Users can query the evidence directly via `/api/chat`. The chat module maintains up to 6 turns of history. 
- **Citations**: Both explanation and chat endpoints generate `[E#]` citation tokens. The frontend maps these tokens to clickable anchors, automatically scrolling the user to the precise `EvidenceCard` that generated the claim.

## Grounding Strategy & Validators
To ensure maximum safety in a health/biomedical context, we deployed strict server-side validators:
1. **Citation Verification**: Any `[E#]` citation hallucinated by the model that does not correspond to an actual retrieved passage is immediately stripped.
2. **Fact/Quote Cross-Checking**: The validator ensures that quantitative figures (e.g., percentages, raw numbers) output by the model literally exist within the provided context text.
3. **Verdict Consistency**: The validator blocks the LLM from outputting statements that flagrantly contradict the ML system's computed verdict.
4. **Fallback Scenarios**: If the LLM generates ungrounded data twice, or if the API key is missing/timeouts, the system gracefully degrades, providing a templated textual summary (e.g., "Analyzed 10 passages from 3 studies...").

## Tech Stack & Configuration
- **Model**: Default `gemini-3.1-flash-lite` (with automatic fallback to `gemini-3.8-flash`, `gemini-3.5-flash`, and `gemma-4-26b-a4b-it`) using `generativelanguage.googleapis.com`.
- **Environment**: Configured via `LLM_PROVIDER`, `GEMINI_API_KEY`, or `LLM_API_KEY`.
- **Frontend**: Integrated via `ClaimChat.jsx` and `ExplanationCard.jsx`.

## Weaknesses
- Complex logic constraints require strong prompt following; weaker models might fail the strict number/verdict validation and repeatedly trigger the fallback template.
- Chat history is hard-capped to 6 turns to avoid context overflow, limiting deep interrogations.
