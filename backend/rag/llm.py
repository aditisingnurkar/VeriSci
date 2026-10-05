import os
import requests
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

FALLBACK_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemma-4-26b-a4b-it"
]

class LLMClient:
    @staticmethod
    def generate(system_prompt, messages, json_schema=None):
        provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
        
        try:
            if provider == "gemini":
                return LLMClient._generate_gemini(system_prompt, messages, json_schema)
            elif provider == "mock":
                return LLMClient._generate_mock(system_prompt, messages, json_schema)
            else:
                logging.warning(f"Unsupported LLM provider: {provider}")
                return None
        except Exception as e:
            logging.error(f"LLM Generation failed: {str(e)}")
            return None
            
    @staticmethod
    def _generate_gemini(system_prompt, messages, json_schema):
        api_key = os.environ.get("GEMINI_API_KEY", os.environ.get("LLM_API_KEY"))
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing")
            
        configured_model = os.environ.get("LLM_MODEL", "gemini-3.1-flash-lite")
        models_to_try = [configured_model] + [m for m in FALLBACK_MODELS if m != configured_model]
        
        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": "SYSTEM INSTRUCTIONS (Follow strictly):\n" + system_prompt}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "Understood. I will strictly follow these instructions and cite using [E#] format."}]
            })
            
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
            
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.1,
            }
        }
        
        if json_schema:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        last_error = None
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            try:
                resp = requests.post(url, json=payload, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                        text = candidates[0]["content"]["parts"][0].get("text", "")
                        return text
                elif resp.status_code in (404, 429, 503):
                    logging.warning(f"Gemini model {model} returned HTTP {resp.status_code}, trying fallback...")
                    last_error = f"HTTP {resp.status_code}: {resp.text[:120]}"
                    continue
                else:
                    resp.raise_for_status()
            except requests.exceptions.RequestException as req_err:
                logging.warning(f"Request to Gemini model {model} failed: {req_err}, trying next candidate...")
                last_error = str(req_err)
                continue

        if last_error:
            raise RuntimeError(f"All Gemini models exhausted. Last error: {last_error}")
        return None

    @staticmethod
    def _generate_mock(system_prompt, messages, json_schema):
        # A simple deterministic mock for testing
        if json_schema:
            return json.dumps({
                "explanation": "This is a mock explanation based on the evidence.",
                "citations": ["E1"],
                "limitations": ["Mock limitations"],
                "answer": "This is a mock answer citing [E1].",
                "answerable": True
            })
        return "This is a mock response citing [E1]."
