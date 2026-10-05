from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import sys
import os
import logging
import uuid
import time
import asyncio

sys.path.append(os.path.dirname(__file__))

from retrieval.retrieve import retrieve_evidence, load_index
from ml.inference import classify_evidence, classifier
from aggregation import aggregate_predictions
from rag.service import explain, chat

# Simple in-memory TTL cache
verification_cache = {}
CACHE_TTL = 3600  # 1 hour

async def cleanup_cache():
    while True:
        await asyncio.sleep(600)  # Cleanup every 10 mins
        now = time.time()
        expired = [k for k, v in verification_cache.items() if now - v['timestamp'] > CACHE_TTL]
        for k in expired:
            del verification_cache[k]

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
        
    # Start cache cleanup task
    task = asyncio.create_task(cleanup_cache())
    yield
    task.cancel()

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

class ExplainRequest(BaseModel):
    verification_id: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    verification_id: str
    message: str
    history: list[ChatMessage] = []

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
    verification_id = str(uuid.uuid4())
    
    try:
        retrieved = retrieve_evidence(claim, top_k=top_k)
        
        sources_used = ["SciFact"]
        if os.environ.get("ENABLE_PUBMED", "false").lower() == "true":
            sources_used.append("PubMed")
        
        if not retrieved:
            result = {
                "verification_id": verification_id,
                "claim": claim,
                "verdict": "INSUFFICIENT",
                "reason_code": "NO_RELEVANT_EVIDENCE",
                "strength": "WEAK",
                "score": 0.0,
                "reason": "We searched our sources and found no relevant studies.",
                "counts": {"support": 0, "contradict": 0, "neutral": 0, "papers": 0},
                "evidence": [],
                "model": {"retriever": "TF-IDF", "classifier": "Linear SVM", "version": "1.0"},
                "sources_used": sources_used
            }
        else:
            if len(retrieved) > 0 and retrieved[0].get("out_of_scope"):
                result = {
                    "verification_id": verification_id,
                    "claim": claim,
                    "verdict": "INSUFFICIENT",
                    "reason_code": "OUT_OF_SCOPE",
                    "strength": "WEAK",
                    "score": 0.0,
                    "reason": "This tool verifies biomedical/health claims. This claim looks outside that scope.",
                    "counts": {"support": 0, "contradict": 0, "neutral": 0, "papers": 0},
                    "evidence": [],
                    "model": {"retriever": "TF-IDF", "classifier": "Linear SVM", "version": "1.0"},
                    "sources_used": sources_used
                }
            else:
                evidence_texts = [ev["evidence_text"] for ev in retrieved]
                ml_results = classify_evidence(claim, evidence_texts)
                
                predictions = []
                for idx, (ev, ml) in enumerate(zip(retrieved, ml_results)):
                    predictions.append({
                        "evidence_id": f"E{idx+1}",
                        "source": ev.get("source", "SciFact"),
                        "source_id": str(ev.get("doc_id", "")),
                        "url": ev.get("url", ""),
                        "title": ev["title"],
                        "evidence_text": ev["evidence_text"],
                        "context_before": ev.get("context_before", ""),
                        "context_after": ev.get("context_after", ""),
                        "sentence_idx": ev.get("sentence_idx", 0),
                        "relevance_score": ev["relevance_score"],
                        "prediction": ml["prediction"],
                        "confidence": ml["confidence"]
                    })
                    
                agg_result = aggregate_predictions(predictions)
                
                result = {
                    "verification_id": verification_id,
                    "claim": claim,
                    "verdict": agg_result["verdict"],
                    "reason_code": "NONE",
                    "strength": agg_result["strength"],
                    "score": agg_result["score"],
                    "reason": agg_result["reason"],
                    "counts": agg_result["counts"],
                    "evidence": predictions,
                    "model": {"retriever": "TF-IDF", "classifier": "Linear SVM", "version": "1.0"},
                    "sources_used": sources_used
                }
                
        # Cache the result
        verification_cache[verification_id] = {
            "timestamp": time.time(),
            "data": result
        }
        
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logging.error(f"Verify error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/classify")
def classify_endpoint(req: ClassifyRequest):
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

@app.post("/api/explain")
def explain_endpoint(req: ExplainRequest):
    verification_data = verification_cache.get(req.verification_id)
    if not verification_data:
        raise HTTPException(status_code=410, detail="Verification session expired. Please re-run verification.")
        
    try:
        result = explain(verification_data["data"])
        return result
    except Exception as e:
        logging.error(f"Explain error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    verification_data = verification_cache.get(req.verification_id)
    if not verification_data:
        raise HTTPException(status_code=410, detail="Verification session expired. Please re-run verification.")
        
    try:
        history = [{"role": m.role, "content": m.content} for m in req.history]
        result = chat(verification_data["data"], history, req.message)
        return result
    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
