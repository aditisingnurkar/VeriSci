import os
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

HEALTHVER_DIR = os.path.join(DATA_DIR, "healthver")
MANCON_DIR = os.path.join(DATA_DIR, "mancon")

DATASETS_URLS = {
    "healthver": {
        "dir": HEALTHVER_DIR,
        "files": {
            "healthver_train.csv": "https://raw.githubusercontent.com/sarrouti/HealthVer/master/data/healthver_train.csv",
            "healthver_dev.csv": "https://raw.githubusercontent.com/sarrouti/HealthVer/master/data/healthver_dev.csv",
            "healthver_test.csv": "https://raw.githubusercontent.com/sarrouti/HealthVer/master/data/healthver_test.csv",
        }
    },
    "mancon": {
        "dir": MANCON_DIR,
        "files": {
            "corpus.xml": "http://staffwww.dcs.shef.ac.uk/people/M.Stevenson/resources/bio_contradictions/corpus.xml"
        }
    }
}

def download_file(url: str, dest_path: str) -> bool:
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        logging.info(f"File already exists: {dest_path} ({os.path.getsize(dest_path)} bytes). Skipping download.")
        return True

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    logging.info(f"Downloading from {url} to {dest_path}...")
    try:
        headers = {"User-Agent": "VeriSci-Dataset-Loader/1.0"}
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=16384):
                if chunk:
                    f.write(chunk)
        logging.info(f"Successfully downloaded {dest_path} ({os.path.getsize(dest_path)} bytes).")
        return True
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")
        return False

def acquire_all_datasets():
    all_success = True
    for ds_name, config in DATASETS_URLS.items():
        logging.info(f"Checking dataset: {ds_name}")
        for filename, url in config["files"].items():
            dest = os.path.join(config["dir"], filename)
            success = download_file(url, dest)
            if not success:
                all_success = False
    return all_success

if __name__ == "__main__":
    success = acquire_all_datasets()
    if success:
        logging.info("All additional datasets acquired successfully.")
    else:
        logging.error("Some dataset downloads failed.")
