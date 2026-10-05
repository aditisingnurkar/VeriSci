import re

def validate_citations(response_json, valid_evidence_ids):
    """
    Ensure all citations in the response are valid.
    Removes invalid citations from the list and from the text.
    """
    citations = response_json.get("citations", [])
    text = response_json.get("explanation", response_json.get("answer", ""))
    
    valid_citations = []
    for c in citations:
        if c in valid_evidence_ids:
            valid_citations.append(c)
        else:
            # Remove from text
            text = text.replace(f"[{c}]", "")
            
    # Also strip any [E#] from text that wasn't properly parsed
    for match in re.findall(r'\[E\d+\]', text):
        clean_match = match.strip("[]")
        if clean_match not in valid_evidence_ids:
            text = text.replace(match, "")
            
    if "explanation" in response_json:
        response_json["explanation"] = text
    else:
        response_json["answer"] = text
        
    response_json["citations"] = list(set(valid_citations))
    return response_json

def validate_numbers_and_quotes(response_text, context_text):
    """
    Check if numbers in the response text actually exist in the context text.
    This is a basic check.
    """
    # Find all numbers
    numbers = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', response_text))
    for num in numbers:
        if num not in context_text:
            return False, f"Number {num} fabricated"
            
    return True, ""

def validate_verdict_consistency(response_text, verdict):
    """
    Basic check to ensure the LLM doesn't contradict the verdict.
    """
    # Simple heuristics
    text = response_text.lower()
    if verdict == "CONTRADICTED":
        if "evidence supports the claim" in text or "proves the claim is true" in text:
            return False, "Contradicts CONTRADICTED verdict"
    elif verdict == "SUPPORTED":
        if "evidence contradicts the claim" in text or "proves the claim is false" in text:
            return False, "Contradicts SUPPORTED verdict"
            
    return True, ""
