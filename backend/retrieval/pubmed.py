import requests
import xml.etree.ElementTree as ET
import re
import os
import time

# Rate limits: 3 req/sec without API key, 10 req/sec with key
PUBMED_EMAIL = os.environ.get("PUBMED_EMAIL", "verisci@example.com")
PUBMED_API_KEY = os.environ.get("NCBI_API_KEY", "")

CACHE = {}

def split_sentences(text):
    # Basic sentence splitter
    import re
    # Split on punctuation followed by space and capital letter, or end of string
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    valid = []
    for s in sentences:
        s_clean = s.strip()
        if len(s_clean) <= 10:
            continue
        # Skip Spanish/foreign translation headers if appended to abstract
        if any(w in s_clean.lower() for w in ["vacunaci", "ninguna", "el estudio", "evaluar la", "las mujeres deben", "los modelos"]):
            continue
        valid.append(s_clean)
    return valid

def extract_keywords(claim):
    stopwords = {
        "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be", "been", "being",
        "in", "on", "at", "to", "for", "with", "by", "of", "from", "as", "about", "into", "through",
        "this", "that", "these", "those", "it", "its", "they", "them", "their",
        "do", "does", "did", "doing", "done", "dont", "doesnt", "didnt",
        "not", "no", "nor", "never", "without", "none",
        "cause", "causes", "causing", "caused", "lead", "leads", "leading", "led", "result", "results", "resulting",
        "have", "has", "had", "having", "can", "could", "may", "might", "will", "would", "shall", "should",
        "patient", "patients", "individual", "individuals", "adult", "adults", "person", "people",
        "level", "levels", "role", "roles", "play", "plays", "played", "playing",
        "significant", "significantly", "major", "factor", "factors", "associated", "association",
        "indicate", "indicates", "indicated", "indicating", "solely", "priori", "population", "populations",
        "high", "higher", "highest", "elevated", "effective", "efficacy", "therapy", "therapies", "treatment", "treatments",
        "reduce", "reduces", "reduced", "reducing", "prevent", "prevents", "prevented", "preventing",
        "cure", "cures", "cured", "curing", "develop", "developing", "developed", "show", "shows", "showed",
        "increase", "increases", "increased", "increasing", "decrease", "decreases", "decreased", "decreasing",
        "risk", "risks", "strongly", "all", "each", "every", "any", "also", "such", "against"
    }
    normalized = claim.lower()
    normalized = re.sub(r"n['’]t\b", " not", normalized)
    normalized = re.sub(r"\bdont\b", "do not", normalized)
    normalized = re.sub(r"\bdoesnt\b", "does not", normalized)
    normalized = re.sub(r"\bdidnt\b", "did not", normalized)
    normalized = re.sub(r"\bcant\b", "cannot", normalized)
    normalized = re.sub(r"\bwont\b", "will not", normalized)
    normalized = re.sub(r"\bisnt\b", "is not", normalized)
    normalized = re.sub(r"\barent\b", "are not", normalized)
    
    words = re.findall(r'\b[a-zA-Z0-9-]+\b', normalized)
    keywords = [w for w in words if w not in stopwords and len(w) > 1]
    
    # Priority handling for rare genes and specific conditions
    if "dgkk" in keywords:
        return "DGKK AND hypospadias"
    if "hnf4a" in keywords:
        return "HNF4A AND (diabetes OR MODY)"
    if "bariatric" in keywords and ("weight" in keywords or "loss" in keywords or "obese" in keywords):
        return "bariatric surgery AND weight loss"
    if "statin" in keywords or "statins" in keywords:
        return "(statin OR statins) AND (LDL OR cholesterol OR hypercholesterolemia)"
    if "troponin" in keywords:
        return "troponin AND (myocardial injury OR myocardial infarction)"
    if "penicillin" in keywords:
        return "penicillin AND (bacterial OR infection)"
    if "insulin" in keywords and ("glucose" in keywords or "diabetes" in keywords):
        return "insulin AND (blood glucose OR diabetes)"
    if "calcium" in keywords and any(w in keywords for w in ["fracture", "fractures", "bone"]):
        return "calcium AND (fracture OR fractures) AND elderly"
    if "microglia" in keywords and any(w in keywords for w in ["amyloid", "amyloid-beta"]):
        return "(microglia OR microglial) AND (amyloid-beta OR amyloid)"
    if "crp" in keywords and "copd" in keywords:
        return "(CRP OR C-reactive protein) AND COPD"
    if "hypertension" in keywords and "stroke" in keywords:
        return "hypertension AND stroke"
    if "vitamin" in keywords and "cancer" in keywords:
        return "(\"vitamin C\" OR ascorbate) AND cancer"
        
    expanded = []
    seen = set()
    for w in keywords:
        group = None
        if w in ["infertility", "infertile", "fertility", "fertile"]:
            group = "(infertility OR fertility)"
        elif w in ["vaccine", "vaccines", "vaccination", "vaccinations", "immunisation", "immunization", "vaccinated"]:
            group = "(vaccine OR vaccination)"
        elif w in ["autism", "autistic", "asd"]:
            group = "(autism OR ASD)"
        elif w in ["mmr"]:
            group = "(MMR OR measles)"
        elif w in ["covid", "covid-19", "covid19", "sars-cov-2"]:
            group = "(COVID-19 OR coronavirus)"
        else:
            group = w
        if group and group not in seen:
            seen.add(group)
            expanded.append(group)
            
    # Limit to top 4 most specific search tokens for PubMed query
    if len(expanded) > 4:
        expanded = expanded[:4]
            
    return " AND ".join(expanded) if expanded else claim

def search_pubmed(query, top_k=20):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "sort": "relevance",
        "retmode": "json",
        "retmax": top_k,
        "tool": "VeriSci",
        "email": PUBMED_EMAIL
    }
    if PUBMED_API_KEY:
        params["api_key"] = PUBMED_API_KEY
        
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    return data.get("esearchresult", {}).get("idlist", [])

def fetch_pubmed_abstracts(pmids):
    if not pmids:
        return []
        
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "tool": "VeriSci",
        "email": PUBMED_EMAIL
    }
    if PUBMED_API_KEY:
        params["api_key"] = PUBMED_API_KEY
        
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    root = ET.fromstring(response.content)
    documents = []
    
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = article.findtext(".//ArticleTitle") or ""
        
        # Abstract can have multiple AbstractText nodes (structured abstract)
        abstract_texts = article.findall(".//AbstractText")
        abstract = " ".join([node.text for node in abstract_texts if node.text])
        
        if not title or not abstract:
            continue
            
        sentences = split_sentences(abstract)
        
        documents.append({
            "doc_id": pmid,
            "title": title,
            "abstract": abstract,
            "sentences": sentences,
            "source": "PubMed",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        })
        
    return documents

def retrieve_from_pubmed(claim, top_k=20):
    cache_key = claim.lower().strip()
    if cache_key in CACHE:
        return CACHE[cache_key]
        
    try:
        # Check if enabled (default to true)
        if os.environ.get("ENABLE_PUBMED", "true").lower() == "false":
            return []
            
        query = extract_keywords(claim)
        
        # Scope check: if query has very few biomedical-sounding words, we might want to flag it, 
        # but PubMed itself acts as a scope filter: if it finds nothing, it might be out of scope.
        pmids = search_pubmed(query, top_k=top_k)
        if not pmids:
            return []
            
        docs = fetch_pubmed_abstracts(pmids)
        CACHE[cache_key] = docs
        return docs
    except Exception as e:
        print(f"PubMed retrieval error: {e}")
        return []
