import os
import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

URLS = {
    "corpus.jsonl": "https://raw.githubusercontent.com/allenai/scifact/master/data/corpus.jsonl",
    "claims_train.jsonl": "https://raw.githubusercontent.com/allenai/scifact/master/data/claims_train.jsonl",
    "claims_dev.jsonl": "https://raw.githubusercontent.com/allenai/scifact/master/data/claims_dev.jsonl"
}

def download_file(filename, url):
    dest = os.path.join(DATA_DIR, filename)
    print(f"Downloading {url} to {dest}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("Download complete.")
    else:
        print(f"Failed to download. HTTP Status: {response.status_code}")

if __name__ == "__main__":
    for filename, url in URLS.items():
        download_file(filename, url)
