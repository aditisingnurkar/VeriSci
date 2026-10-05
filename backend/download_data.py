import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_mock_scifact():
    print("Generating local SciFact corpus for testing...")
    corpus_path = os.path.join(DATA_DIR, "corpus.jsonl")
    
    # Mocking actual SciFact schema: doc_id, title, abstract (list of strings), structured
    corpus_data = [
        {
            "doc_id": 1,
            "title": "Systematic review of COVID-19 vaccination and fertility",
            "abstract": [
                "There have been concerns about the effect of COVID-19 vaccines on fertility.",
                "Our comprehensive analysis of clinical data indicates no negative impact of the SARS-CoV-2 vaccine on male or female fertility parameters.",
                "Vaccines are safe and do not cause infertility."
            ],
            "structured": False
        },
        {
            "doc_id": 2,
            "title": "Impact of vaccines on reproductive health: A longitudinal study",
            "abstract": [
                "We studied the pregnancy rates among vaccinated cohorts compared to placebo.",
                "Pregnancy rates were identical among the vaccinated cohort compared to the placebo group.",
                "No evidence of infertility was observed across the cohorts."
            ],
            "structured": False
        },
        {
            "doc_id": 3,
            "title": "Climate change and ocean temperatures",
            "abstract": [
                "Global warming has significantly increased ocean temperatures.",
                "This has led to coral bleaching and loss of marine biodiversity.",
                "Human carbon emissions are the primary driver of this warming."
            ],
            "structured": False
        },
        {
            "doc_id": 4,
            "title": "Vitamin C and the common cold",
            "abstract": [
                "Vitamin C has long been touted as a cure for the common cold.",
                "However, randomized controlled trials show that high doses of Vitamin C do not cure the common cold.",
                "It may only slightly reduce the duration of symptoms."
            ],
            "structured": False
        },
        {
            "doc_id": 5,
            "title": "Artificial sweeteners and cancer risk",
            "abstract": [
                "Early animal studies suggested a link between artificial sweeteners and cancer.",
                "Modern epidemiological studies have found no conclusive evidence that eating artificial sweeteners increases the risk of cancer in humans."
            ],
            "structured": False
        }
    ]
    
    with open(corpus_path, 'w', encoding='utf-8') as f:
        for doc in corpus_data:
            f.write(json.dumps(doc) + '\n')
            
    print(f"Generated {len(corpus_data)} corpus documents at {corpus_path}")

if __name__ == "__main__":
    generate_mock_scifact()
