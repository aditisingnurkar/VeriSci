import json
import logging
from .llm import LLMClient
from .prompts import SYSTEM_PROMPT, EXPLAIN_PROMPT, CHAT_PROMPT
from .context import build_context
from .validators import validate_citations, validate_numbers_and_quotes, validate_verdict_consistency

def explain(verification_data):
    context = build_context(verification_data)
    prompt = EXPLAIN_PROMPT.replace("{context}", context)
    
    valid_evidence_ids = [ev["evidence_id"] for ev in verification_data.get("evidence", [])]
    
    if verification_data.get("verdict") == "INSUFFICIENT":
        return {
            "explanation": f"The system found no relevant evidence or determined this claim is out of scope. {verification_data.get('reason', '')}",
            "citations": [],
            "limitations": ["No evidence retrieved."]
        }
    
    # Try twice
    for attempt in range(2):
        try:
            raw_response = LLMClient.generate(SYSTEM_PROMPT, [{"role": "user", "content": prompt}], json_schema=True)
            if not raw_response:
                raise ValueError("LLM returned empty response")
                
            # clean backticks if present
            raw_response = raw_response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            response_json = json.loads(raw_response)
            
            # Validations
            response_json = validate_citations(response_json, valid_evidence_ids)
            num_valid, msg = validate_numbers_and_quotes(response_json.get("explanation", ""), context)
            if not num_valid:
                logging.warning(f"Validation failed (numbers): {msg}")
                continue
                
            ver_valid, msg = validate_verdict_consistency(response_json.get("explanation", ""), verification_data.get("verdict"))
            if not ver_valid:
                logging.warning(f"Validation failed (verdict): {msg}")
                continue
                
            return response_json
            
        except Exception as e:
            logging.error(f"Explanation generation attempt {attempt + 1} failed: {e}")
            
    # Fallback template
    return _fallback_explanation(verification_data)

def _fallback_explanation(verification_data):
    verdict = verification_data.get("verdict")
    reason = verification_data.get("reason")
    counts = verification_data.get("counts", {})
    
    explanation = f"The automated system analyzed {counts.get('support',0) + counts.get('contradict',0) + counts.get('neutral',0)} passages from {counts.get('papers', 0)} studies. "
    explanation += f"Based on its classification, it determined the claim is {verdict} because: {reason}. "
    explanation += "(AI Explanation unavailable - using fallback template)."
    
    return {
        "explanation": explanation,
        "citations": [],
        "limitations": ["AI explanation generation failed.", "Relies on classical classification pipeline alone."]
    }

def chat(verification_data, history, message):
    context = build_context(verification_data)
    prompt = CHAT_PROMPT.replace("{context}", context)
    
    valid_evidence_ids = [ev["evidence_id"] for ev in verification_data.get("evidence", [])]
    
    messages = [{"role": "user", "content": prompt}]
    # Add history
    for h in history[-6:]: # cap to 6 turns
        messages.append({"role": h["role"], "content": h["content"]})
        
    messages.append({"role": "user", "content": message})
    
    for attempt in range(2):
        try:
            raw_response = LLMClient.generate(SYSTEM_PROMPT, messages, json_schema=True)
            if not raw_response:
                raise ValueError("LLM returned empty response")
                
            raw_response = raw_response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            response_json = json.loads(raw_response)
            
            if not response_json.get("answerable", True):
                response_json["answer"] = "The retrieved evidence doesn't say."
                response_json["citations"] = []
                return response_json
                
            # Validations
            response_json = validate_citations(response_json, valid_evidence_ids)
            num_valid, msg = validate_numbers_and_quotes(response_json.get("answer", ""), context)
            if not num_valid:
                logging.warning(f"Validation failed (numbers): {msg}")
                continue
                
            ver_valid, msg = validate_verdict_consistency(response_json.get("answer", ""), verification_data.get("verdict"))
            if not ver_valid:
                logging.warning(f"Validation failed (verdict): {msg}")
                continue
                
            # Format citations to be objects instead of strings
            citation_objects = []
            for cid in response_json.get("citations", []):
                for ev in verification_data.get("evidence", []):
                    if ev.get("evidence_id") == cid:
                        citation_objects.append({
                            "evidence_id": cid,
                            "title": ev.get("title", ""),
                            "source": ev.get("source", "SciFact"),
                            "source_id": str(ev.get("source_id", ev.get("doc_id", ""))),
                            "url": ev.get("url", "")
                        })
                        break
            response_json["citations"] = citation_objects
            return response_json
            
        except Exception as e:
            logging.error(f"Chat generation attempt {attempt + 1} failed: {e}")
            
    return {
        "answer": "I'm sorry, but I am currently unavailable to answer questions.",
        "citations": [],
        "answerable": False
    }

