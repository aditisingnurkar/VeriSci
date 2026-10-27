from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import sys
import os
import json
import logging
import uuid
import time
import asyncio
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(__file__))

from retrieval.retrieve import retrieve_evidence, load_index
from retrieval.spelling import check_claim_spelling
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

# Allow frontend requests from any local/dev origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClaimRequest(BaseModel):
    claim: str
    top_k: int = 5

class SpellCheckRequest(BaseModel):
    claim: str

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

@app.get("/health")
def health_endpoint():
    return {"status": "ok", "model": "Unsupervised K-Means (k=3) + Sentence-Transformers"}

@app.get("/api/health")
def api_health():
    return {"status": "ok"}

@app.post("/api/retrieve")
def retrieve(req: ClaimRequest):
    claim = req.claim.strip()
    if not claim or len(claim) > 1000:
        raise HTTPException(status_code=400, detail="Claim length invalid")
    
    top_k = min(max(req.top_k, 1), 20)
    try:
        results = retrieve_evidence(claim, top_k=top_k)
        if len(results) > 0 and results[0].get("out_of_scope"):
            return {"evidence": [], "out_of_scope": True}
        return {"evidence": results}
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Index not built yet.")
    except Exception as e:
        logging.error(f"Retrieve error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/spellcheck")
def spellcheck_endpoint(req: SpellCheckRequest):
    claim = req.claim.strip()
    if not claim or len(claim) > 1000:
        raise HTTPException(status_code=400, detail="Claim length invalid")
    return check_claim_spelling(claim)

@app.post("/api/verify")
def verify(req: ClaimRequest):
    claim = req.claim.strip()
    if not claim or len(claim) > 1000:
        raise HTTPException(status_code=400, detail="Claim length invalid")
        
    top_k = min(max(req.top_k, 1), 20)
    verification_id = str(uuid.uuid4())
    
    # Check spelling conservatively without modifying original claim
    spelling_info = check_claim_spelling(claim)
    
    try:
        retrieved = retrieve_evidence(claim, top_k=top_k)
        
        # If no evidence found or retrieval missed live medical sources due to typos in key terms, attempt safe retrieval expansion
        if spelling_info["has_suggestion"] and spelling_info["is_safe"]:
            has_pubmed = any(ev.get("source") == "PubMed" for ev in retrieved) if retrieved else False
            if not retrieved or not has_pubmed:
                suggested_retrieved = retrieve_evidence(spelling_info["suggested_claim"], top_k=top_k)
                if suggested_retrieved and not suggested_retrieved[0].get("out_of_scope"):
                    if not retrieved or any(ev.get("source") == "PubMed" for ev in suggested_retrieved):
                        retrieved = suggested_retrieved
                        spelling_info["applied_to_retrieval"] = True
        
        sources_used = ["SciFact"]
        if os.environ.get("ENABLE_PUBMED", "true").lower() != "false":
            sources_used.append("PubMed")
        
        classifier_meta = "Unsupervised K-Means (k=3) + Sentence-Transformers (all-MiniLM-L6-v2)"
        
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
                "spelling_suggestion": spelling_info,
                "model": {"retriever": "SciFact TF-IDF + PubMed Live", "classifier": classifier_meta, "version": "2.0-Unsupervised"},
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
                    "spelling_suggestion": spelling_info,
                    "model": {"retriever": "SciFact TF-IDF + PubMed Live", "classifier": classifier_meta, "version": "2.0-Unsupervised"},
                    "sources_used": sources_used
                }
            else:
                evidence_texts = [ev["evidence_text"] for ev in retrieved]
                titles = [ev.get("title", "") for ev in retrieved]
                eval_claim = spelling_info["suggested_claim"] if (spelling_info.get("applied_to_retrieval") or (spelling_info.get("has_suggestion") and spelling_info.get("is_safe"))) else claim
                ml_results = classify_evidence(eval_claim, evidence_texts, titles=titles)
                
                predictions = []
                for idx, (ev, ml) in enumerate(zip(retrieved, ml_results)):
                    predictions.append({
                        "evidence_id": f"E{idx+1}",
                        "source": ev.get("source", "SciFact"),
                        "doc_id": str(ev.get("doc_id", "")),
                        "source_id": str(ev.get("doc_id", "")),
                        "url": ev.get("url", ""),
                        "title": ev["title"],
                        "evidence_text": ev["evidence_text"],
                        "context_before": ev.get("context_before", ""),
                        "context_after": ev.get("context_after", ""),
                        "sentence_idx": ev.get("sentence_idx", 0),
                        "relevance_score": ev["relevance_score"],
                        "prediction": ml["prediction"],
                        "confidence": ml["confidence"],
                        "cluster_id": ml.get("cluster_id", 0),
                        "centroid_distance": ml.get("centroid_distance", 0.0),
                        "cluster_affinity": ml.get("cluster_affinity", ml.get("confidence", 0.5)),
                        "is_unsupervised": True,
                        "stance_source": ml.get("stance_source", "unsupervised_cluster_mapping"),
                        "validation_purity": ml.get("validation_purity", 0.5),
                        "all_distances": ml.get("all_distances", [])
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
                    "spelling_suggestion": spelling_info,
                    "model": {"retriever": "SciFact TF-IDF + PubMed Live", "classifier": classifier_meta, "version": "2.0-Unsupervised"},
                    "sources_used": sources_used,
                    "unsupervised_diagnostics": {
                        "dominant_cluster": agg_result.get("dominant_cluster", -1),
                        "cluster_weights": agg_result.get("cluster_weights", {}),
                        "methodology": agg_result.get("methodology", "Unsupervised K-Means")
                    }
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
        import traceback
        traceback.print_exc()
        logging.error(f"Verify error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get("/api/comparison")
def comparison_endpoint():
    """
    Returns empirical benchmark results comparing Supervised Random Forest vs. Unsupervised K-Means.
    """
    results_path = os.path.join(os.path.dirname(__file__), "eval", "unsupervised_comparison_results.json")
    if not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Comparison benchmark results not found.")
    try:
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"Comparison endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load comparison results: {str(e)}")

