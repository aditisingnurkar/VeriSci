import json
import os

def load_corpus(corpus_path):
    """
    Reads the SciFact corpus.jsonl file.
    Returns a list of dictionaries, where each dict is a sentence/passage.
    """
    passages = []
    if not os.path.exists(corpus_path):
        raise FileNotFoundError(f"Corpus file not found: {corpus_path}")
        
    with open(corpus_path, 'r', encoding='utf-8') as f:
        for line in f:
            doc = json.loads(line)
            doc_id = doc['doc_id']
            title = doc['title']
            abstract = doc.get('abstract', [])
            
            for idx, sentence in enumerate(abstract):
                passages.append({
                    "id": f"{doc_id}_{idx}",
                    "doc_id": doc_id,
                    "title": title,
                    "sentence_idx": idx,
                    "text": sentence
                })
    return passages
