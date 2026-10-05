import os
import sys
import json
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from sklearn.metrics import classification_report, f1_score, confusion_matrix
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ml.dataset import get_train_dev_data

def evaluate_transformer():
    print("Loading dev set...")
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    _, dev_df = get_train_dev_data(DATA_DIR)
    
    model_name = "cross-encoder/nli-distilroberta-base"
    print(f"Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    
    id2label = model.config.id2label
    print(f"id2label: {id2label}")
    
    # Typical distilroberta-base NLI mapping: 0: contradiction, 1: entailment, 2: neutral
    # We will adjust dynamically based on id2label keys
    label_map = {}
    for id, label in id2label.items():
        if "contradiction" in label.lower():
            label_map[id] = "CONTRADICT"
        elif "entailment" in label.lower() or "support" in label.lower():
            label_map[id] = "SUPPORT"
        else:
            label_map[id] = "NEUTRAL"
            
    y_true = []
    y_pred = []
    
    batch_size = 16
    for i in tqdm(range(0, len(dev_df), batch_size)):
        batch = dev_df.iloc[i:i+batch_size]
        claims = batch['claim'].tolist()
        evidences = batch['evidence_text'].tolist()
        
        inputs = tokenizer(claims, evidences, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            preds = torch.argmax(outputs.logits, dim=1).numpy()
            
        for pred, true_label in zip(preds, batch['label']):
            pred_label = label_map.get(pred, 'NEUTRAL')
            y_pred.append(pred_label)
            y_true.append(true_label)
            
    print(classification_report(y_true, y_pred))
    macro_f1 = f1_score(y_true, y_pred, average='macro')
    print(f"Macro F1: {macro_f1:.4f}")
    print("Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred, labels=["SUPPORT", "CONTRADICT", "NEUTRAL"]))
    
if __name__ == "__main__":
    evaluate_transformer()
