import os
import requests
import zipfile
from io import BytesIO

DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(MODEL_DIR, "SMSSpamCollection")

def download_and_extract_data():
    if os.path.exists(DATA_FILE):
        print(f"Dataset already exists at {DATA_FILE}")
        return

    print(f"Downloading dataset from {DATASET_URL}...")
    response = requests.get(DATASET_URL)
    response.raise_for_status()

    print("Extracting dataset...")
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        z.extractall(MODEL_DIR)
    
    print(f"Dataset extracted to {MODEL_DIR}")

if __name__ == "__main__":
    download_and_extract_data()
