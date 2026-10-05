import os
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

URLS = {
    "corpus.jsonl": ("https://raw.githubusercontent.com/allenai/scifact/master/data/corpus.jsonl", 5183),
    "claims_train.jsonl": ("https://raw.githubusercontent.com/allenai/scifact/master/data/claims_train.jsonl", 809),
    "claims_dev.jsonl": ("https://raw.githubusercontent.com/allenai/scifact/master/data/claims_dev.jsonl", 300),
    "claims_test.jsonl": ("https://raw.githubusercontent.com/allenai/scifact/master/data/claims_test.jsonl", 300)
}

def download_file(filename, url):
    dest = os.path.join(DATA_DIR, filename)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        logging.info(f"File {filename} already exists and is non-empty. Skipping download.")
        return dest
        
    logging.info(f"Downloading {url} to {dest}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logging.info("Download complete.")
        return dest
    else:
        logging.error(f"Failed to download. HTTP Status: {response.status_code}")
        return None

def verify_counts(filename, expected_count):
    dest = os.path.join(DATA_DIR, filename)
    if not os.path.exists(dest):
        logging.error(f"File {filename} not found for verification.")
        return False
        
    count = 0
    with open(dest, 'r', encoding='utf-8') as f:
        for _ in f:
            count += 1
            
    if count == expected_count:
        logging.info(f"{filename} verified: count matches {expected_count}")
        return True
    else:
        logging.error(f"{filename} count mismatch: expected {expected_count}, got {count}")
        return False

def main():
    success = True
    for filename, (url, expected_count) in URLS.items():
        if download_file(filename, url):
            if not verify_counts(filename, expected_count):
                success = False
        else:
            success = False
            
    if success:
        logging.info("All files downloaded and verified successfully.")
    else:
        logging.error("Some files failed to download or verify.")

if __name__ == "__main__":
    main()
