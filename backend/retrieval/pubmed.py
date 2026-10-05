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
    return [s.strip() for s in sentences if len(s.strip()) > 5]

def extract_keywords(claim):
    # Very basic extraction - remove common stopwords and punctuation
    stopwords = {"a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "in", "on", "at", "to", "for", "with", "by", "of", "this", "that", "it"}
    words = re.findall(r'\b[a-zA-Z0-9-]+\b', claim.lower())
    keywords = [w for w in words if w not in stopwords]
    return " ".join(keywords)

def search_pubmed(query, top_k=20):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
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
        # Check if enabled
        if os.environ.get("ENABLE_PUBMED", "false").lower() != "true":
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
