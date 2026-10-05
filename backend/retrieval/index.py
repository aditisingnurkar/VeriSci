import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from preprocess import load_corpus

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CORPUS_PATH = os.path.join(DATA_DIR, "corpus.jsonl")
INDEX_DIR = os.path.join(os.path.dirname(__file__), "saved_index")

def build_index():
    os.makedirs(INDEX_DIR, exist_ok=True)
    
    print("Loading corpus...")
    passages = load_corpus(CORPUS_PATH)
    
    print(f"Loaded {len(passages)} sentences. Building TF-IDF index...")
    
    # Extract texts for vectorization
    texts = [p['text'] for p in passages]
    
    vectorizer = TfidfVectorizer(stop_words='english', max_df=0.8, min_df=1)
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    print("Saving vectorizer and matrix...")
    with open(os.path.join(INDEX_DIR, 'vectorizer.pkl'), 'wb') as f:
        pickle.dump(vectorizer, f)
        
    with open(os.path.join(INDEX_DIR, 'tfidf_matrix.pkl'), 'wb') as f:
        pickle.dump(tfidf_matrix, f)
        
    with open(os.path.join(INDEX_DIR, 'passages.pkl'), 'wb') as f:
        pickle.dump(passages, f)
        
    print("Index built and saved successfully.")

if __name__ == "__main__":
    build_index()
