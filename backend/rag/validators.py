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
    Check if statistical numbers/percentages in the response text actually exist in the context text.
    """
    # Remove citation IDs like [E1], [E2] before checking numbers
    clean_resp = re.sub(r'\[E\d+\]', '', response_text)
    
    # Word to number equivalents
    word_to_num = {
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
        "twenty-nine": "29", "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50"
    }
    
    context_lower = context_text.lower()
    for word, digit in word_to_num.items():
        if word in context_lower:
            context_lower += f" {digit} {digit}%"
            
    # Find numbers and percentages
    numbers = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', clean_resp))
    for num in numbers:
        # Allow small cardinal counts 1..10 in natural explanations
        clean_num = num.rstrip('%')
        try:
            if float(clean_num) <= 10 and '%' not in num:
                continue
        except ValueError:
            pass
            
        if num.lower() not in context_lower and clean_num not in context_lower:
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
