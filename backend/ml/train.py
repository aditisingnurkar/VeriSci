import os
import pickle
import argparse
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC, SVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ml.dataset import get_train_dev_data, get_three_dataset_data
from ml.features import FeatureExtractor

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

def evaluate_model(model_name, model, X_test, y_test):
    y_pred = model.predict(X_test)
    print(f"\n--- {model_name} ---")
    print(classification_report(y_test, y_pred, digits=4))
    
    # Calculate Macro F1 explicitly
    macro_f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
    print(f"Macro F1: {macro_f1:.4f}")
    
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred, labels=["SUPPORT", "CONTRADICT", "NEUTRAL"]))
    return macro_f1

def train_pipeline(three_datasets=True):
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    if three_datasets:
        print("Loading Three-Dataset Combined Data (SciFact + HealthVer + ManConCorpus)...")
        train_df, dev_df = get_three_dataset_data(DATA_DIR)
    else:
        print("Loading SciFact-only Data...")
        train_df, dev_df = get_train_dev_data(DATA_DIR)

    print(f"Train size: {len(train_df)}")
    print(f"Dev size: {len(dev_df)}")
    
    print("Class distribution in Train:")
    print(train_df['label'].value_counts())
    
    print("\nExtracting features...")
    extractor = FeatureExtractor()
    extractor.fit(train_df['claim'], train_df['evidence_text'])
    
    X_train = extractor.transform(train_df['claim'], train_df['evidence_text'])
    y_train = train_df['label']
    
    X_dev = extractor.transform(dev_df['claim'], dev_df['evidence_text'])
    y_dev = dev_df['label']
    
    print("\nTraining models...")
    
    # Use LinearSVC with dual=False for fast linear SVM on larger datasets
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
        "Linear SVM": CalibratedClassifierCV(LinearSVC(dual=False, class_weight='balanced', random_state=42), cv=2),
        "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1)
    }
    
    best_f1 = 0
    best_model_name = ""
    best_model = None
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        f1 = evaluate_model(name, model, X_dev, y_dev)
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = model
            
    print(f"\nBest Model: {best_model_name} with Macro F1: {best_f1:.4f}")
    
    # Save the best model and vectorizer
    print("Saving the best model and feature extractor...")
    with open(os.path.join(MODELS_DIR, 'evidence_classifier.pkl'), 'wb') as f:
        pickle.dump(best_model, f)
    with open(os.path.join(MODELS_DIR, 'feature_extractor.pkl'), 'wb') as f:
        pickle.dump(extractor, f)
        
    print("Training pipeline complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VeriSci Stance Classification Training Pipeline")
    parser.add_argument("--scifact-only", action="store_true", help="Train on SciFact only")
    args = parser.parse_args()
    train_pipeline(three_datasets=not args.scifact_only)

