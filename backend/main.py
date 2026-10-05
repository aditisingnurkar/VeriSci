from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import sys
import os
import logging

sys.path.append(os.path.dirname(__file__))

from retrieval.retrieve import retrieve_evidence, load_index
from ml.inference import classify_evidence, classifier
from aggregation import aggregate_predictions

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        load_index()
    except Exception as e:
        logging.warning(f"Could not load index on startup. {e}")
    try:
        classifier.load()
    except Exception as e:
        logging.warning(f"Could not load classifier on startup. {e}")
    yield

app = FastAPI(title="VeriSci Backend", lifespan=lifespan)

# Allow frontend requests
FRONTEND_URL = os.getenv("VITE_API_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClaimRequest(BaseModel):
    claim: str
    top_k: int = 5

class ClassifyRequest(BaseModel):
    claim: str
    evidence: list[str]

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/retrieve")
def retrieve(req: ClaimRequest):
    claim = req.claim.strip()
    if not claim or len(claim) > 1000:
        raise HTTPException(status_code=400, detail="Claim length invalid")
    
    top_k = min(max(req.top_k, 1), 20)
    try:
        results = retrieve_evidence(claim, top_k=top_k)
        return {"evidence": results}
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Index not built yet.")
    except Exception as e:
        logging.error(f"Retrieve error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/verify")
def verify(req: ClaimRequest):
    claim = req.claim.strip()
    if not claim or len(claim) > 1000:
        raise HTTPException(status_code=400, detail="Claim length invalid")
        
    top_k = min(max(req.top_k, 1), 20)
    try:
        retrieved = retrieve_evidence(claim, top_k=top_k)
        
        if not retrieved:
            return {
                "claim": claim,
                "verdict": "INSUFFICIENT",
                "strength": "WEAK",
                "score": 0.0,
                "reason": "No relevant evidence found.",
                "counts": {"support": 0, "contradict": 0, "neutral": 0, "papers": 0},
                "evidence": [],
                "model": {"retriever": "TF-IDF", "classifier": "Linear SVM", "version": "1.0"}
            }
            
        evidence_texts = [ev["evidence_text"] for ev in retrieved]
        ml_results = classify_evidence(claim, evidence_texts)
        
        predictions = []
        for ev, ml in zip(retrieved, ml_results):
            predictions.append({
                "doc_id": ev["doc_id"],
                "title": ev["title"],
                "evidence_text": ev["evidence_text"],
                "sentence_idx": ev.get("sentence_idx", 0),
                "relevance_score": ev["relevance_score"],
                "source": ev["source"],
                "prediction": ml["prediction"],
                "confidence": ml["confidence"]
            })
            
        agg_result = aggregate_predictions(predictions)
        
        return {
            "claim": claim,
            "verdict": agg_result["verdict"],
            "strength": agg_result["strength"],
            "score": agg_result["score"],
            "reason": agg_result["reason"],
            "counts": agg_result["counts"],
            "evidence": predictions,
            "model": {"retriever": "TF-IDF", "classifier": "Linear SVM", "version": "1.0"}
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logging.error(f"Verify error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/classify")
def classify(req: ClassifyRequest):
    claim = req.claim.strip()
    if not claim or len(claim) > 1000:
        raise HTTPException(status_code=400, detail="Claim length invalid")
        
    try:
        results = classify_evidence(claim, req.evidence)
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
        logging.error(f"Classify error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
