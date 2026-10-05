import os
import sys
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from preprocess import load_documents

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CORPUS_PATH = os.path.join(DATA_DIR, "corpus.jsonl")
INDEX_DIR = os.path.join(os.path.dirname(__file__), "saved_index")

def build_index():
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    print("Loading documents from corpus...")
    documents = load_documents(CORPUS_PATH)
    
    print(f"Loaded {len(documents)} documents. Building document TF-IDF index...")
    
    # We will build a doc-level vectorizer
    doc_texts = [d['text'] for d in documents]
    
    doc_vectorizer = TfidfVectorizer(
        stop_words='english', 
        ngram_range=(1, 2), 
        sublinear_tf=True, 
        max_df=0.8, 
        min_df=2
    )
    doc_tfidf_matrix = doc_vectorizer.fit_transform(doc_texts)
    
    print("Saving index...")
    with open(os.path.join(INDEX_DIR, 'doc_vectorizer.pkl'), 'wb') as f:
        pickle.dump(doc_vectorizer, f)
        
    with open(os.path.join(INDEX_DIR, 'doc_tfidf_matrix.pkl'), 'wb') as f:
        pickle.dump(doc_tfidf_matrix, f)
        
    with open(os.path.join(INDEX_DIR, 'documents.pkl'), 'wb') as f:
        pickle.dump(documents, f)
        
    print("Index built and saved successfully.")

if __name__ == "__main__":
    build_index()
