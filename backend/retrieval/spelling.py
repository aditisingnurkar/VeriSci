import os
import inspect
import pickle
import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Meaning-critical scientific and negation terms that must NEVER be altered
PROTECTED_TERMS = {
    # Negation words
    "not", "no", "never", "without", "none", "neither", "nor", "cannot", "doesnt", "didnt", 
    "wont", "isnt", "arent", "wasnt", "werent", "hardly", "scarcely", "barely",
    # Directional / causal scientific verbs
    "increase", "increases", "increased", "increasing",
    "decrease", "decreases", "decreased", "decreasing",
    "reduce", "reduces", "reduced", "reducing", "reduction",
    "elevate", "elevates", "elevated", "elevating",
    "lower", "lowers", "lowered", "lowering",
    "cause", "causes", "caused", "causing",
    "prevent", "prevents", "prevented", "preventing", "prevention",
    "promote", "promotes", "promoted", "promoting",
    "inhibit", "inhibits", "inhibited", "inhibiting", "inhibition",
    "induce", "induces", "induced", "inducing",
    "associate", "associated", "associates", "associating", "association",
    "correlate", "correlated", "correlates", "correlating", "correlation",
    # Modals / quantifiers
    "all", "every", "some", "any", "may", "can", "could", "might", "must", "should", "only"
}

_sym_spell = None
_biomedical_vocab = None

def get_sym_spell():
    """
    Initializes SymSpell with English frequency dictionary and verified biomedical terms.
    Cached as a singleton.
    """
    global _sym_spell, _biomedical_vocab
    if _sym_spell is not None:
        return _sym_spell

    try:
        import symspellpy
        from symspellpy import SymSpell
        
        sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        sym_dir = os.path.dirname(inspect.getfile(symspellpy))
        dict_path = os.path.join(sym_dir, 'frequency_dictionary_en_82_765.txt')
        
        if os.path.exists(dict_path):
            sym_spell.load_dictionary(dict_path, term_index=0, count_index=1)
        else:
            logger.warning(f"SymSpell frequency dictionary not found at {dict_path}")

        # Common biomedical and dietary/clinical words to prioritize over general slang
        COMMON_HEALTH_TERMS = [
            "sugar", "glucose", "insulin", "diabetes", "diabetic", "vaccine", "vaccines", "vaccination",
            "autism", "cholesterol", "metformin", "hypertension", "cardiovascular", "myocardial",
            "infarction", "coronary", "artery", "carcinoma", "lymphoma", "leukemia", "chemotherapy",
            "antibiotic", "antibiotics", "antiviral", "respiratory", "pulmonary", "pneumonia",
            "inflammation", "inflammatory", "cellular", "molecular", "genetic", "epigenetic",
            "mortality", "morbidity", "prevalence", "incidence", "prognosis", "diagnosis",
            "efficacy", "toxicity", "adverse", "syndrome", "disorder", "pathology", "pathogen"
        ]
        for term in COMMON_HEALTH_TERMS:
            sym_spell.create_dictionary_entry(term, 100000000)
            sym_spell.words[term] = 100000000

        # Seed with biomedical terms from the SciFact corpus vectorizer if available
        index_dir = os.path.join(os.path.dirname(__file__), "saved_index")
        vec_path = os.path.join(index_dir, "doc_vectorizer.pkl")
        _biomedical_vocab = set()
        
        if os.path.exists(vec_path):
            with open(vec_path, "rb") as f:
                vec = pickle.load(f)
            for term in vec.vocabulary_.keys():
                term_clean = term.lower().strip()
                if len(term_clean) > 2 and term_clean.isalpha():
                    _biomedical_vocab.add(term_clean)
                    # Add with high frequency count so valid biomedical words are preferred
                    sym_spell.create_dictionary_entry(term_clean, 50000)
                    
        # Also ensure all protected terms are in the dictionary with high frequency
        for term in PROTECTED_TERMS:
            sym_spell.create_dictionary_entry(term, 1000000)
            
        _sym_spell = sym_spell
        return _sym_spell
    except Exception as e:
        logger.error(f"Failed to initialize SymSpell: {e}")
        return None

def check_claim_spelling(claim: str) -> Dict[str, Any]:
    """
    Conservatively checks a claim for typos without modifying meaning-critical words.
    
    Returns:
        {
            "has_suggestion": bool,
            "original_claim": str,
            "suggested_claim": str,
            "corrections": [
                {"original": "metfomin", "suggested": "metformin", "position": 0}
            ],
            "is_safe": bool
        }
    """
    if not claim or not claim.strip():
        return {
            "has_suggestion": False,
            "original_claim": claim,
            "suggested_claim": claim,
            "corrections": [],
            "is_safe": True
        }

    sym_spell = get_sym_spell()
    if sym_spell is None:
        return {
            "has_suggestion": False,
            "original_claim": claim,
            "suggested_claim": claim,
            "corrections": [],
            "is_safe": True
        }

    from symspellpy import Verbosity

    # Tokenize words while preserving punctuation and spacing
    tokens = re.findall(r"\b[A-Za-z\-']+\b|\s+|[^\w\s]", claim)
    corrected_tokens = []
    corrections = []
    
    for token in tokens:
        # Only evaluate pure alphabetic words of length >= 4
        clean_word = token.strip().lower()
        
        if not clean_word.isalpha() or len(clean_word) < 4:
            corrected_tokens.append(token)
            continue
            
        # NEVER alter protected terms (negations, direction, causal verbs)
        if clean_word in PROTECTED_TERMS:
            corrected_tokens.append(token)
            continue
            
        # Check if the word is already a known word in SymSpell or Biomedical vocabulary
        if clean_word in sym_spell.words or (_biomedical_vocab and clean_word in _biomedical_vocab):
            corrected_tokens.append(token)
            continue
            
        # Check for candidates within edit distance <= 2
        suggestions = sym_spell.lookup(clean_word, Verbosity.CLOSEST, max_edit_distance=2)
        valid_suggestions = [
            s for s in suggestions
            if s.term != clean_word and s.term not in PROTECTED_TERMS
        ]
        
        if valid_suggestions:
            def rank_candidate(s):
                # 1. Edit distance (lower is better)
                dist = s.distance
                # 2. Priority for verified health / biomedical curated vocabulary (count >= 50,000,000)
                is_curated_health = 0 if s.count >= 50000000 else 1
                # 3. Suffix agreement (e.g. 'vacins' ends in 's', so prefer 'vaccines' over 'vaccine')
                suffix_match = 0 if (clean_word.endswith('s') == s.term.endswith('s')) else 1
                # 4. Higher frequency count (negate count)
                neg_count = -s.count
                # 5. Length proximity
                len_diff = abs(len(s.term) - len(clean_word))
                return (dist, is_curated_health, suffix_match, neg_count, len_diff)

            valid_suggestions.sort(key=rank_candidate)
            best = valid_suggestions[0].term
            
            # Preserve original capitalization
            if token.isupper():
                suggested_word = best.upper()
            elif token[0].isupper():
                suggested_word = best.capitalize()
            else:
                suggested_word = best
                
            corrected_tokens.append(suggested_word)
            corrections.append({
                "original": token,
                "suggested": suggested_word
            })
            continue
                
        corrected_tokens.append(token)
        
    suggested_claim = "".join(corrected_tokens)
    has_suggestion = len(corrections) > 0 and (suggested_claim != claim)
    
    return {
        "has_suggestion": has_suggestion,
        "original_claim": claim,
        "suggested_claim": suggested_claim,
        "corrections": corrections,
        "is_safe": True
    }
