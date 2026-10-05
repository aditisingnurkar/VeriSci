import json
import os

def load_documents(corpus_path):
    """
    Reads the SciFact corpus.jsonl file.
    Returns a list of dictionaries, where each dict is a document with sentences.
    """
    documents = []
    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"Corpus file not found: {corpus_path}")
        
    with open(corpus_path, 'r', encoding='utf-8') as f:
        for line in f:
            doc = json.loads(line)
            doc_id = doc['doc_id']
            title = doc['title']
            abstract = doc.get('abstract', [])
            
            # Document text for doc-level retrieval
            doc_text = title + " " + " ".join(abstract)
            
            documents.append({
                "doc_id": doc_id,
                "title": title,
                "text": doc_text,
                "sentences": abstract
            })
    return documents
