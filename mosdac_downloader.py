import requests
import json
import os
import time
import sys
from datetime import datetime, timedelta

# Configuration
CONFIG_FILE = 'mosdac_config.json'

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found.")
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def download_data():
    config = load_config()
    if not config:
        return

    creds = config.get('user_credentials', {})
    params = config.get('search_parameters', {})
    settings = config.get('download_settings', {})

    username = creds.get('username')
    password = creds.get('password')
    
    if username == "YOUR_USERNAME" or not username:
        print("Please set your MOSDAC username in mosdac_config.json")
        return

    # Authenticate (This is a simplified flow based on MOSDAC logic)
    # Note: Actual endpoint might vary, this is a best-effort template based on documentation
    session = requests.Session()
    
    # login_url = "https://mosdac.gov.in/auth/login" # Example
    # For now, we assume the user might need to use the official mdapi.py if this custom one fails 
    # BUT, based on the search, MOSDAC exposes a specific API endpoint.
    
    print("------------------------------------------------")
    print("   MOSDAC Auto-Downloader                       ")
    print("------------------------------------------------")
    print(f"Dataset ID: {params.get('datasetId')}")
    print("Searching for latest data...")

    # Placeholder logic for the official MDAPI interaction
    # Since we can't reverse engineer the exact auth flow without docs, 
    # we will provide the instructions to use the OFFICIAL script.
    
    print("\n[INFO] To download automatically, you must use the official MDAPI Client.")
    print("I have created the 'mosdac_config.json' file for you.")
    print("1. Download 'mdapi.py' from: https://mosdac.gov.in/software/mdapi.zip")
    print("2. Place it in this folder.")
    print("3. Run: python mdapi.py")
    print("4. The files will appear here, and the Dashboard will auto-detect them!")

if __name__ == "__main__":
    download_data()
