# Phase 1: Complete Frontend/UI

## Objective
Create a polished, modern, and trustworthy frontend for VeriSci (Evidence-Based Scientific Claim Verification). This phase implements the complete user interface flow using mock data to represent the eventual ML and retrieval outputs. It sets up the foundation for future backend integration.

## UI Architecture
The application is built as a Single Page Application (SPA) using React, Vite, and Tailwind CSS. The design follows a modular component-based architecture with clean, scientific styling suitable for a data-verification tool. State is passed via React Router's location state between pages to simulate a workflow.

## Pages Created
- **Home (`src/pages/Home.jsx`)**: The landing page featuring branding, a tagline, a claim input area, and clickable example claims.
- **Analysis (`src/pages/Analysis.jsx`)**: A loading/transition page that simulates the backend processing steps (Searching Evidence, Analyzing Evidence, Preparing Verdict) with clear visual indicators.
- **Results (`src/pages/Results.jsx`)**: The primary results dashboard displaying the overall verdict, evidence summary, ML analysis, human-readable explanation, and a placeholder for the "Ask about this claim" contextual chat.

## Components Created
- **`Navbar.jsx`**: Top navigation with branding.
- **`Footer.jsx`**: Simple footer with copyright info.
- **`ClaimInput.jsx`**: The main search/input field for claims.
- **`ExampleClaims.jsx`**: A list of clickable example claims.
- **`AnalysisProgress.jsx`**: A visual step-by-step progress indicator for the loading state.
- **`VerdictCard.jsx`**: Displays the final aggregated verdict (e.g., LIKELY CONTRADICTED) and confidence score.
- **`EvidenceSummary.jsx`**: A high-level count of supporting, contradicting, and neutral evidence.
- **`EvidenceCard.jsx`**: A reusable card showing a retrieved paper's title, snippet, prediction, confidence, and source.
- **`MLAnalysis.jsx`**: A section breaking down the ML model's prediction for each individual evidence passage.
- **`ExplanationCard.jsx`**: A dedicated section for the human-readable explanation (RAG placeholder).
- **`ClaimChat.jsx`**: A mock chat interface for asking context-specific questions about the claim.

## Files Created
- `frontend/src/data/mockData.js`
- `frontend/src/pages/Home.jsx`, `Analysis.jsx`, `Results.jsx`
- `frontend/src/components/*.jsx`
- `frontend/src/lib/utils.js` (for Tailwind class merging)
- `docs/phase-1.md`

## Files Modified
- `frontend/vite.config.js`: Updated to support Tailwind CSS v4.
- `frontend/src/index.css`: Updated with Tailwind v4 imports and base styles.
- `frontend/src/App.jsx`: Wrapped the application in React Router and defined routes.

## Dependencies Added
- `react-router-dom`: For client-side routing.
- `lucide-react`: For clean, modern SVG icons.
- `tailwindcss` (v4) and `@tailwindcss/vite`: For utility-first styling.
- `clsx` and `tailwind-merge`: For dynamic component styling logic.

## Routing
- `/`: Home Page
- `/analyze`: Analysis/Loading State
- `/results`: Verification Results Dashboard

## Mock Data Structure
A centralized `mockData.js` provides realistic representations of future API responses.
- `claim`: string
- `verdict`: string
- `verdictConfidence`: number
- `supportingCount`, `contradictingCount`, `neutralCount`: numbers
- `explanation`: string
- `evidence`: Array of objects containing `id`, `title`, `snippet`, `prediction`, `confidence`, `relevanceScore`, and `source`.

## Responsive Behavior
- Built using mobile-first Tailwind utilities.
- Important UI sections (like the Results layout) collapse gracefully from multi-column grids on desktop to stacked columns on mobile devices.
- No horizontal overflow on smaller screens.

## Accessibility
- Proper contrast ratios are maintained using standard Tailwind colors.
- Semantic HTML tags (`<nav>`, `<main>`, `<footer>`, `<h1>`, `<h2>`) are utilized.
- Form controls are labeled and usable via keyboard.

## Testing Performed
- **Build test**: Verified the project compiles perfectly without TS/React errors (`npm run build`).
- **UI/Routing test**: Verified routes connect properly from Home -> Analyze -> Results.
- **Component test**: Ensured all components render their assigned mock data correctly.

## Known Limitations
- State is currently isolated to individual page sessions via `useLocation().state` rather than a global context or server cache.
- The chat interface is purely a static UI placeholder with no logic.
- Real processing times and error states (e.g., API failures) are only simulated.

## What belongs to later phases
- **Phase 2 (Retrieval)**: Replacing mock evidence generation with actual SciFact TF-IDF retrieval.
- **Phase 3 (ML)**: Training and integrating the evidence classifier.
- **Phase 4 (Aggregation)**: Implementing real backend logic to combine evidence into a verdict.
- **Phase 5 (RAG)**: Integrating an LLM to power the explanation and chat interfaces.
- Real backend API (FastAPI) integration.

## How Phase 2 will connect to the UI
Phase 2 will introduce the FastAPI backend and scientific evidence retrieval. The frontend's `ClaimInput` submission will be updated to send an HTTP request to the new FastAPI backend, which will return real SciFact documents. We will map this real data into the `evidence` arrays currently mocked in the frontend to display actual retrieved papers in the `EvidenceCard` and `EvidenceSummary` components.
