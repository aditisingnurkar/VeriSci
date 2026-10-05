import json
import os
import pandas as pd
import random
import sys
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from retrieval.retrieve import retrieve_evidence

def load_corpus(corpus_path):
    corpus = {}
    with open(corpus_path, 'r', encoding='utf-8') as f:
        for line in f:
            doc = json.loads(line)
            corpus[str(doc['doc_id'])] = doc
    return corpus

def build_dataset(claims_path, corpus, include_hard_negatives=False):
    data = []
    with open(claims_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in tqdm(lines, desc=f"Building dataset for {os.path.basename(claims_path)}"):
            claim_data = json.loads(line)
            claim = claim_data['claim']
            evidence = claim_data.get('evidence', {})
            cited_doc_ids = claim_data.get('cited_doc_ids', [])
            
            gold_sentences = set()
            
            # Evidence rationales
            for doc_id, rationales in evidence.items():
                doc_id = str(doc_id)
                if doc_id not in corpus:
                    continue
                
                abstract = corpus[doc_id]['abstract']
                evidence_sentences = set()
                
                # Extract SUPPORT / CONTRADICT
                for rationale in rationales:
                    label = rationale['label']
                    for sent_idx in rationale['sentences']:
                        evidence_sentences.add(sent_idx)
                        gold_sentences.add((doc_id, sent_idx))
                        if sent_idx < len(abstract):
                            data.append({
                                'claim': claim,
                                'evidence_text': abstract[sent_idx],
                                'label': label
                            })
                
                # Extract NEUTRAL (sentences in the same doc)
                neutral_cands = [i for i in range(len(abstract)) if i not in evidence_sentences]
                if neutral_cands:
                    sampled = random.sample(neutral_cands, min(2, len(neutral_cands)))
                    for sent_idx in sampled:
                        data.append({
                            'claim': claim,
                            'evidence_text': abstract[sent_idx],
                            'label': 'NEUTRAL'
                        })
            
            # Pure neutral documents cited
            for doc_id in cited_doc_ids:
                doc_id = str(doc_id)
                if doc_id not in evidence and doc_id in corpus:
                    abstract = corpus[doc_id]['abstract']
                    if abstract:
                        sent_idx = random.randint(0, len(abstract) - 1)
                        data.append({
                            'claim': claim,
                            'evidence_text': abstract[sent_idx],
                            'label': 'NEUTRAL'
                        })
            
            if include_hard_negatives:
                retrieved = retrieve_evidence(claim, top_k=5, doc_threshold=0.01, sent_threshold=0.01)
                for res in retrieved:
                    doc_id = res['doc_id']
                    sent_idx = res['sentence_idx']
                    if (doc_id, sent_idx) not in gold_sentences:
                        data.append({
                            'claim': claim,
                            'evidence_text': res['evidence_text'],
                            'label': 'NEUTRAL'
                        })

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=['claim', 'evidence_text'])
    return df

def get_train_dev_data(data_dir):
    random.seed(42)
    corpus_path = os.path.join(data_dir, 'corpus.jsonl')
    train_path = os.path.join(data_dir, 'claims_train.jsonl')
    dev_path = os.path.join(data_dir, 'claims_dev.jsonl')
    
    corpus = load_corpus(corpus_path)
    train_df = build_dataset(train_path, corpus, include_hard_negatives=True)
    dev_df = build_dataset(dev_path, corpus, include_hard_negatives=True)
    
    return train_df, dev_df
