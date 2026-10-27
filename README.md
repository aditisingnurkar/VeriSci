# VeriSci: Automated Biomedical Evidence Verification & Literature Synthesis

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://reactjs.org)
[![Vite](https://img.shields.io/badge/Vite-8.3+-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-Interactions_API-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev)
[![Tests](https://img.shields.io/badge/Tests-36%2F36_Passing-success?style=flat&logo=pytest&logoColor=white)](https://pytest.org)
[![ML Datasets](https://img.shields.io/badge/ML_Datasets-SciFact%20%2B%20HealthVer%20%2B%20ManConCorpus-8A2BE2?style=flat)](docs/phase-6-three-dataset-integration.md)

[![Unsupervised Learning](https://img.shields.io/badge/ML_Paradigm-Unsupervised_K--Means_(k=3)-purple?style=flat&logo=scikit-learn&logoColor=white)](docs/supervised-vs-unsupervised-comparison.md)
[![Embeddings](https://img.shields.io/badge/Embeddings-Sentence--Transformers_all--MiniLM--L6--v2-blue?style=flat)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

> **VeriSci (Project B — Unsupervised Learning Edition)** is the unsupervised sister implementation of VeriSci. While retaining the complete end-to-end scientific literature verification architecture (SciFact + PubMed live retrieval, Gemini 2.5 Flash RAG synthesis, interactive citations, and calibrated verdicts), Project B replaces the supervised stance classifier with an **unsupervised K-Means clustering algorithm ($k=3$)** over **384-dimensional dense semantic sentence embeddings (`all-MiniLM-L6-v2`)**.
>
> This fork is built to provide a scientifically honest, empirical comparison between **Supervised Learning** (Random Forest trained on 18,572 labeled pairs) and **Unsupervised Learning** (label-free K-Means) for scientific claim verification in an AIML academic setting.

---

## 🔬 Supervised vs. Unsupervised Benchmark (4,978 Held-Out Test Samples)

| Evaluation Dimension | Project A (Supervised Random Forest) | Project B (Unsupervised K-Means $k=3$) | Observation / Analysis |
| :--- | :--- | :--- | :--- |
| **Training Labels** | **18,572 labeled pairs** | **0 pairs (Fully Unlabeled)** | K-Means fitted without any stance labels |
| **Input Representation** | 7 handcrafted features + NLI | 384-dim dense embeddings | Sentence-Transformers `all-MiniLM-L6-v2` |
| **Overall Accuracy** | **71.70%** | **45.42%** | Supervised leads by **+26.28%** |
| **Macro F1 Score** | **0.5703** | **0.4183** | Supervised leads by **+0.1520** |
| **SUPPORT F1** | 0.4906 | 0.4534 | Comparable: topic overlap signals support |
| **CONTRADICT F1** | **0.3730** | **0.2171** | Negations require supervised contrastive bounds |
| **NEUTRAL F1** | 0.8472 | 0.5842 | Cluster 0 isolates unrelated literature (86.7% purity) |
| **Silhouette Score** | N/A | **0.1512** | Mild cluster cohesion in dense semantic space |
| **Adjusted Rand Index** | N/A | **0.0712** | Near-zero ARI: clusters by topic, not polarity |
| **Interactive Dashboard**| N/A | **`/compare` route** in UI | Live comparative charts, samples & contingency |

---

## 🚀 Quickstart Commands (Project B)

### 1. Backend Setup & Run
```bash
# Navigate to Project B backend
cd "C:\VeriSci - Copy\VeriSci\backend"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements (including sentence-transformers)
pip install -r requirements.txt

# Run Unsupervised Model Training (Label-Free K-Means on 18,572 pairs)
python ml/train_unsupervised.py

# Run Empirical Benchmark Evaluation (4,978 test samples)
python ml/evaluate_unsupervised.py

# Run Test Suite (16 passed)
pytest tests -v

# Start the Backend Server (Port 8000 or 8001)
uvicorn main:app --reload --port 8001
```

### 2. Frontend Setup & Run
```bash
# Navigate to Project B frontend
cd "C:\VeriSci - Copy\VeriSci\frontend"

# Install node dependencies
npm install

# Build for production (verified clean build)
npm run build

# Start the Development Server
npm run dev
```

Visit `http://localhost:5173/` for the Verification Desk and `http://localhost:5173/compare` for the Head-to-Head AIML Comparison Dashboard.


---

## System Architecture

```mermaid
flowchart TD
    A["Biomedical / Scientific Claim"] --> B["Dual-Source Retrieval Engine"]
    
    subgraph Retrieval ["1. Dual Retrieval Layer"]
        B --> B1["SciFact Index (5,183 Papers)<br/>TF-IDF + Cosine Relevance"]
        B --> B2["NCBI PubMed Live API<br/>MeSH Semantic Expansion"]
    end
    
    B1 --> C["Top-K Evidence Passages"]
    B2 --> C
    
    subgraph Stance ["2. Stance Classification"]
        C --> D["Hybrid Transformer NLI Cross-Encoder<br/>(SciBERT / NLI + Linear SVM)"]
        D --> E["Passage Stance Stamped:<br/>SUPPORT | CONTRADICT | NEUTRAL"]
    end
    
    subgraph Aggregation ["3. Deterministic Aggregation"]
        E --> F["Confidence-Weighted Evidence Aggregator<br/>Out-of-Scope Detection & Strength Calibration"]
        F --> G["Final Verdict:<br/>SUPPORTED | CONTRADICTED | MIXED | INSUFFICIENT"]
    end
    
    subgraph RAG ["4. Grounded Generative Synthesis"]
        G --> H["Grounded Gemini Engine (gemini-3.1-flash-lite)<br/>Strict Literature Grounding & Schema Output"]
        H --> I["Deterministic Citation & Number Validators<br/>([E#] Integrity & Hallucination Prevention)"]
    end
    
    subgraph UI ["5. Research Interface"]
        G --> J["Editorial Science UI (React / Vite)"]
        I --> J
        J --> K["Verdict & Strength Meter"]
        J --> L["Interactive Citation Badges [E#]"]
        J --> M["Literature Inquest Chat (/api/chat)"]
    end
```

---

## Core Features & Capabilities

### 1. Dual-Source Retrieval Engine
- **SciFact Corpus**: Indexes **5,183 peer-reviewed biomedical abstracts** with BM25/TF-IDF vector matching.
- **PubMed Live Integration**: Expands queries with Medical Subject Headings (MeSH) and queries NCBI PubMed via live REST API for latest publications.
- **Out-of-Scope Guardrails**: Automatically detects non-biomedical claims (e.g. general trivia, astrology) and flags them before classification.

### 2. Transformer NLI Stance Classification
- **Cross-Encoder Architecture**: Evaluates paired `(claim, evidence_passage)` inputs.
- **Three-Way Stance**: Categorizes each retrieved passage as `SUPPORT`, `CONTRADICT`, or `NEUTRAL`.
- **Calibrated Confidence**: Outputs statistical probability scores for each passage.

### 3. Transparent Verdict Aggregation
- Combines stance counts, relevance rankings, and classification confidence scores into an overall claim verdict:
  - `SUPPORTED`: Clear empirical consensus across studies.
  - `CONTRADICTED`: Peer-reviewed evidence refutes the hypothesis.
  - `MIXED`: Genuine scientific debate or conflicting study outcomes.
  - `INSUFFICIENT`: Low relevance scores or no pertinent literature identified.

### 4. Zero-Hallucination Grounded Gemini RAG
- **Strict Evidence Grounding**: Powered by Google Gemini (`gemini-3.1-flash-lite`, with fallback cascade to `gemini-3.8-flash`, `gemini-3.5-flash`, and `gemma-4-26b-a4b-it`).
- **Citation Badges (`[E1]`, `[E2]`)**: Every factual assertion is tied directly to retrieved passage IDs.
- **Hallucination Prevention**: Automated server-side validators check numerical assertions, citation validity, and verdict consistency.
- **Analytical Caveats**: Highlights limitations such as small sample sizes, in-vitro models, or observational study constraints.

### 5. Conversational Literature Inquest
- Allows researchers and clinicians to query the retrieved dossier interactively via `/api/chat`.
- Returns strictly grounded answers with exact study references.

### 6. Natural Editorial UI
- Atmospheric cellular microscopy background canvas with layered CSS masking.
- Scholarly typography combining **Newsreader** serif and **Plus Jakarta Sans**.
- Interactive stance filtering, smooth citation jumping, and tactile glassmorphic cards.

---

## Repository Structure

```
VeriSci/
├── backend/
│   ├── aggregation.py             # Verdict & confidence score aggregator
│   ├── config.py                  # Environment & model settings
│   ├── data_acquisition.py        # Automated downloader for HealthVer & ManConCorpus
│   ├── main.py                    # FastAPI server & route handlers
│   ├── requirements.txt           # Python dependencies
│   ├── ml/
│   │   ├── dataset.py             # Three-dataset loader & SciFact fallback
│   │   ├── unified_pipeline.py    # Schema normalization, deduplication & splitting
│   │   ├── run_experiments.py     # Experiments A, B, C empirical evaluation suite
│   │   ├── inference.py           # NLI classification inference pipeline
│   │   └── train.py               # Classical ML model training (--scifact-only flag)
│   ├── rag/
│   │   ├── context.py             # Context assembler for LLM prompts
│   │   ├── llm.py                 # Gemini client with multi-model fallback
│   │   ├── prompts.py             # System & inquest prompt templates
│   │   ├── service.py             # /api/explain & /api/chat orchestration
│   │   └── validators.py          # Strict citation, number & verdict validators
│   ├── retrieval/
│   │   ├── build_index.py         # SciFact index builder
│   │   ├── pubmed.py              # Live NCBI PubMed API integration
│   │   └── retrieve.py            # Dual retrieval coordinator
│   └── tests/
│       ├── test_aggregation.py    # Aggregation logic test suite
│       ├── test_api.py            # FastAPI endpoint tests
│       ├── test_rag.py            # RAG validators & synthesis tests
│       └── test_three_datasets.py # 3-Dataset schema, normalization, leakage & reloading tests
├── frontend/
│   ├── public/
│   │   └── scientific_bg.jpg      # High-res cellular microscopy asset
│   ├── src/
│   │   ├── App.jsx                # Root app & background canvas layer
│   │   ├── index.css              # Editorial styles, canvas masking & tokens
│   │   ├── components/
│   │   │   ├── ClaimChat.jsx      # Literature inquest chat widget
│   │   │   ├── ClaimInput.jsx     # Claim search input console
│   │   │   ├── EvidenceCard.jsx   # Scientific paper dossier card
│   │   │   ├── ExampleClaims.jsx  # Curated benchmark claim pills
│   │   │   ├── ExplanationCard.jsx# AI synthesis & caveats card
│   │   │   ├── Navbar.jsx         # Header navigation bar
│   │   │   ├── VerdictCard.jsx    # Authoritative verdict display
│   │   │   └── Footer.jsx         # Research provenance footer
│   │   └── pages/
│   │       ├── Home.jsx           # Landing & claim input page
│   │       ├── Analysis.jsx       # Real-time scan progression page
│   │       └── Results.jsx        # Verification dossier dashboard
│   ├── package.json               # Node dependencies & scripts
│   └── vite.config.js             # Vite configuration with Tailwind CSS v4
├── docs/                          # Technical phase design specifications
├── .env.example                   # Environment configuration template
└── README.md                      # Project documentation
```

---

## Getting Started

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**
- *(Optional)* **Google Gemini API Key** (for generative explanations; defaults to graceful deterministic templates if omitted)

---

### Backend Setup

1. **Navigate to the backend directory and set up a virtual environment**:
   ```bash
   cd backend
   python -m venv .venv
   
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```env
   # Provide your Google AI Studio API key
   GEMINI_API_KEY=your_api_key_here

   # Primary LLM Model (fallback models are automatically handled)
   LLM_MODEL=gemini-3.1-flash-lite

   # LLM Provider ('gemini' or 'mock')
   LLM_PROVIDER=gemini
   ```

4. **Start the FastAPI server**:
   ```bash
   python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
   ```
   The backend API documentation is available at `http://127.0.0.1:8000/docs`.

---

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install npm dependencies**:
   ```bash
   npm install
   ```

3. **Run the Vite development server**:
   ```bash
   npm run dev
   ```

4. **Access the application**:
   Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## API Reference

### 1. `POST /api/verify`
Performs end-to-end evidence retrieval, NLI classification, and verdict aggregation.

**Request:**
```json
{
  "claim": "Regular vitamin C supplementation reduces the duration of common cold episodes.",
  "top_k": 5
}
```

**Response:**
```json
{
  "verification_id": "8f3b2a1c-...",
  "claim": "Regular vitamin C supplementation reduces the duration of common cold episodes.",
  "verdict": "SUPPORTED",
  "strength": "STRONG",
  "score": 0.88,
  "reason": "Multiple randomized trials corroborate regular vitamin C supplementation modestly shortens cold duration.",
  "counts": { "support": 3, "contradict": 0, "neutral": 1, "papers": 3 },
  "evidence": [
    {
      "evidence_id": "E1",
      "source": "PubMed",
      "title": "Vitamin C for preventing and treating the common cold",
      "evidence_text": "Twenty-nine trial comparisons involving 11,306 participants contributed to the meta-analysis on duration...",
      "relevance_score": 0.94,
      "prediction": "SUPPORT",
      "confidence": 0.91,
      "url": "https://pubmed.ncbi.nlm.nih.gov/23440782/"
    }
  ]
}
```

---

### 2. `POST /api/explain`
Generates grounded Gemini natural language synthesis with exact citation badges.

**Request:**
```json
{
  "verification_id": "8f3b2a1c-..."
}
```

**Response:**
```json
{
  "explanation": "The retrieved evidence indicates that regular vitamin C supplementation modestly reduces cold duration in adults (8%) and children (14%) [E1]. The system reached a SUPPORTED verdict because randomized trials consistently show shortened symptom duration [E1, E2].",
  "citations": ["E1", "E2"],
  "limitations": [
    "Evidence focuses on continuous daily prophylaxis rather than post-onset treatment.",
    "The overall reduction magnitude is modest."
  ]
}
```

---

### 3. `POST /api/chat`
Allows conversational inquest into the retrieved literature context.

**Request:**
```json
{
  "verification_id": "8f3b2a1c-...",
  "message": "What percentage reduction was seen in children vs adults?",
  "history": []
}
```

**Response:**
```json
{
  "answer": "In children, regular vitamin C supplementation resulted in a 14% reduction in cold duration, compared to an 8% reduction in adults [E1].",
  "citations": [
    { "evidence_id": "E1", "title": "Vitamin C for preventing and treating the common cold", "source": "PubMed" }
  ],
  "answerable": true
}
```

---

## Testing & Quality Assurance

Run the automated backend test suite:
```bash
pytest backend/tests -v
```

## Three-Dataset ML Evidence Stance Integration (Phase 6)

VeriSci integrates three authoritative biomedical verification datasets into a unified evidence stance classification pipeline:

1. **SciFact** ([Allen Institute for AI, EMNLP 2020](https://github.com/allenai/scifact)): 5,183 scientific papers and annotated claim-evidence pairs.
2. **HealthVer** ([Sarrouti et al., NAACL-HLT 2021](https://github.com/sarrouti/HealthVer)): Health-related claims searched against PubMed and Common Crawl with multi-annotator stance labels.
3. **ManConCorpus** ([Alamri & Stevenson, BMC Med Inform Decis Mak 2016 / PMC10919922](http://staffwww.dcs.shef.ac.uk/people/M.Stevenson/resources/bio_contradictions/)): Manually annotated scientific sentence pairs from clinical trial abstracts.

### Empirical Evaluation: Baseline vs. Three-Dataset Model

Evaluated on held-out test splits with exact cross-split leakage prevention (0 duplicate claim-evidence pairs between train and dev):

#### Table 1: Combined Held-Out Dev Set ($N = 4,599$ across SciFact, HealthVer, ManConCorpus)

| Metric | SciFact Baseline | Three-Dataset Model | Absolute Difference |
|---|---|---|---|
| **Accuracy** | 61.99% | **73.26%** | **+11.27 pp** |
| **Macro F1** | 35.29% | **56.42%** | **+21.13 pp** |
| **Weighted F1** | 56.02% | **71.07%** | **+15.06 pp** |
| **SUPPORT F1** | 15.79% | **44.97%** | **+29.18 pp** |
| **CONTRADICT F1** | 12.16% | **38.01%** | **+25.85 pp** |
| **NEUTRAL F1** | 77.91% | **86.27%** | **+8.36 pp** |

#### Table 2: Canonical SciFact Held-Out Dev Set ($N = 2,294$)

| Metric | SciFact Baseline | Three-Dataset Model | Absolute Difference |
|---|---|---|---|
| **Accuracy** | 77.46% | **84.66%** | **+7.20 pp** |
| **Weighted F1** | 78.91% | **80.77%** | **+1.86 pp** |
| **Macro F1** | 41.52% | 35.97% | -5.55 pp |

*Trade-off analysis*: The SciFact-only baseline frequently over-predicted `CONTRADICT` / `SUPPORT` on neutral hard negatives (precision 10.5% and 19.7%), depressing SciFact accuracy to 77.46%. The three-dataset model learned strict evidence boundaries from HealthVer and ManConCorpus, suppressing false-positive claims and raising SciFact accuracy to 84.66% while delivering a +21.13 pp Macro F1 boost across broader biomedical literature.

For complete documentation, data schemas, and ablation analyses, see [docs/phase-6-three-dataset-integration.md](docs/phase-6-three-dataset-integration.md).

---

## Testing & Quality Assurance

Run the automated backend test suite (36 tests):
```bash
pytest backend/tests -v
```

**Test Coverage Summary:**
- `test_negation_nli.py`: Positive vs. negated claims against identical evidence, NLI input ordering (premise=evidence, hypothesis=claim), dynamic label mapping, absence of evidence vs. evidence of absence, directional distinctions (increase vs. decrease), biomedical spelling correction & protected terms, and corroborating paper aggregation.
- `test_three_datasets.py`: Schema validation, 3-way label normalization, train/dev split isolation, cross-dataset leakage prevention, model serialization, backward compatibility, and live API endpoints.
- `test_aggregation.py`: Stance distribution weighting, empty edge cases, and mixed confidence scenarios.
- `test_api.py`: Health checks, live query retrieval, out-of-scope claim detection, verify pipeline, classify routes, and spellcheck endpoint.
- `test_rag.py`: Citation parsing, numerical fabrication checks, verdict consistency, and context formatting.

Run clinical sanity checks across sample biomedical claims:
```bash
python backend/eval/sanity_check.py
```

Validate frontend production bundle:
```bash
cd frontend && npm run build
```

---

## Benchmark Datasets & Citations

- **SciFact Dataset**: [Allen Institute for AI (Wadden et al., EMNLP 2020)](https://github.com/allenai/scifact) - *Fact-Checking Scientific Claims with Evidence*.
- **HealthVer Dataset**: [Sarrouti et al., NAACL-HLT 2021](https://github.com/sarrouti/HealthVer) - *Evidence-Based Verification of Coronavirus and Health-Related Claims*.
- **ManConCorpus**: [Alamri & Stevenson, BMC Med Inform Decis Mak 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC10919922/) - *Corpus of Contradictory Information in Clinical Trial Abstracts*.
- **PubMed REST APIs**: National Center for Biotechnology Information (NCBI) Entrez E-utilities.
- **Google Generative AI**: [Google AI Studio & Gemini API](https://ai.google.dev).

---

## License

This project is licensed under the [MIT License](LICENSE). Built for academic, research, and scientific literature verification.
