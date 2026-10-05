from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os

# Add the parent directory to the path so we can import retrieval
sys.path.append(os.path.dirname(__file__))

from retrieval.retrieve import retrieve_evidence, load_index
from ml.inference import classify_evidence
from aggregation import aggregate_predictions

app = FastAPI(title="VeriSci Backend - Phase 2")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClaimRequest(BaseModel):
    claim: str
    top_k: int = 5

class ClassifyRequest(BaseModel):
    claim: str
    evidence: list[str]

@app.on_event("startup")
def startup_event():
    try:
        # Preload the index so first request is fast
        load_index()
    except Exception as e:
        print(f"Warning: Could not load index on startup. {e}")

@app.post("/api/retrieve")
def retrieve(req: ClaimRequest):
    if not req.claim.strip():
        raise HTTPException(status_code=400, detail="Claim cannot be empty")
        
    try:
        results = retrieve_evidence(req.claim, top_k=req.top_k)
        return {"evidence": results}
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Index not built yet.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/verify")
def verify(req: ClaimRequest):
    if not req.claim.strip():
        raise HTTPException(status_code=400, detail="Claim cannot be empty")
        
    try:
        # Phase 2: Retrieve
        retrieved = retrieve_evidence(req.claim, top_k=req.top_k)
        
        if not retrieved:
            return {
                "claim": req.claim,
                "verdict": "INCONCLUSIVE",
                "confidence": 0.0,
                "evidence": [],
                "supportingCount": 0,
                "contradictingCount": 0,
                "neutralCount": 0
            }
            
        evidence_texts = [ev["evidence_text"] for ev in retrieved]
        
        # Phase 3: Classify
        ml_results = classify_evidence(req.claim, evidence_texts)
        
        # Combine retrieve and ML results for aggregation
        predictions = []
        for ev, ml in zip(retrieved, ml_results):
            predictions.append({
                "document_id": ev["document_id"],
                "title": ev["title"],
                "evidence_text": ev["evidence_text"],
                "relevance_score": ev["relevance_score"],
                "source": ev["source"],
                "prediction": ml["prediction"],
                "confidence": ml["confidence"]
            })
            
        # Phase 4: Aggregate
        agg_result = aggregate_predictions(predictions)
        
        return {
            "claim": req.claim,
            "verdict": agg_result["verdict"],
            "confidence": agg_result["confidence"],
            "evidence": predictions,
            "supportingCount": agg_result["supporting_count"],
            "contradictingCount": agg_result["contradicting_count"],
            "neutralCount": agg_result["neutral_count"]
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/classify")
def classify(req: ClassifyRequest):
    if not req.claim.strip():
        raise HTTPException(status_code=400, detail="Claim cannot be empty")
        
    try:
        results = classify_evidence(req.claim, req.evidence)
        # Format the output to map each evidence string to its prediction
        formatted_results = []
        for ev, res in zip(req.evidence, results):
            formatted_results.append({
                "evidence": ev,
                "prediction": res["prediction"],
                "confidence": res["confidence"]
            })
        return formatted_results
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model not trained yet.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
