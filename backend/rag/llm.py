import os
import requests
import json
import logging

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
            
        model = os.environ.get("LLM_MODEL", "gemini-2.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": "SYSTEM PROMPT (Strictly follow this):\n" + system_prompt}]
            })
            contents.append({
                "role": "model",
                "parts": [{"text": "I will follow these system instructions."}]
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
                "temperature": 0.0,
            }
        }
        
        if json_schema:
            payload["generationConfig"]["responseMimeType"] = "application/json"
            # Very basic mapping of schema if needed, otherwise rely on the prompt to output JSON
            
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text

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
