import json
import os
import pandas as pd
import random

def load_corpus(corpus_path):
    corpus = {}
    with open(corpus_path, 'r', encoding='utf-8') as f:
        for line in f:
            doc = json.loads(line)
            corpus[str(doc['doc_id'])] = doc
    return corpus

def build_dataset(claims_path, corpus):
    data = []
    with open(claims_path, 'r', encoding='utf-8') as f:
        for line in f:
            claim_data = json.loads(line)
            claim = claim_data['claim']
            evidence = claim_data.get('evidence', {})
            cited_doc_ids = claim_data.get('cited_doc_ids', [])
            
            # Evidence contains dict: {doc_id: [{"sentences": [sent_idx], "label": "SUPPORT/CONTRADICT"}]}
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
                        if sent_idx < len(abstract):
                            data.append({
                                'claim': claim,
                                'evidence_text': abstract[sent_idx],
                                'label': label
                            })
                
                # Extract NEUTRAL (sentences in the same doc that are not evidence)
                # To avoid huge class imbalance, let's take a sample of neutral sentences
                neutral_cands = [i for i in range(len(abstract)) if i not in evidence_sentences]
                if neutral_cands:
                    # Take at most 2 neutral sentences per evidence document
                    sampled = random.sample(neutral_cands, min(2, len(neutral_cands)))
                    for sent_idx in sampled:
                        data.append({
                            'claim': claim,
                            'evidence_text': abstract[sent_idx],
                            'label': 'NEUTRAL'
                        })
            
            # For documents cited but completely unrelated to evidence (pure neutral documents)
            for doc_id in cited_doc_ids:
                doc_id = str(doc_id)
                if doc_id not in evidence and doc_id in corpus:
                    abstract = corpus[doc_id]['abstract']
                    # Sample 1 sentence from purely neutral cited documents
                    if abstract:
                        sent_idx = random.randint(0, len(abstract) - 1)
                        data.append({
                            'claim': claim,
                            'evidence_text': abstract[sent_idx],
                            'label': 'NEUTRAL'
                        })

    return pd.DataFrame(data)

def get_train_dev_data(data_dir):
    random.seed(42)
    corpus_path = os.path.join(data_dir, 'corpus.jsonl')
    train_path = os.path.join(data_dir, 'claims_train.jsonl')
    dev_path = os.path.join(data_dir, 'claims_dev.jsonl')
    
    corpus = load_corpus(corpus_path)
    train_df = build_dataset(train_path, corpus)
    dev_df = build_dataset(dev_path, corpus)
    
    return train_df, dev_df
