import json
import subprocess
import sys
import os
from datetime import datetime, timedelta

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def update_config():
    """Updates config.json to search for data from Yesterday and Today."""
    if not os.path.exists(CONFIG_PATH):
        print("Error: config.json not found!")
        return False

    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        # Calculate dynamic dates
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Update parameters
        # Note: We use yesterday as start to ensure we catch late-night uploads from previous day
        config['search_parameters']['startTime'] = yesterday
        config['search_parameters']['endTime'] = today
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
            
        print(f"✅ Configuration updated for: {yesterday} to {today}")
        return True
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

def run_downloader():
    """Runs the official mdapi.py script."""
    print("🚀 Starting MOSDAC Downloader...")
    # Use the same python interpreter that is running this script
    cmd = [sys.executable, "mdapi.py"]
    subprocess.run(cmd)

def run_full_sync():
    """Updates config and runs the downloader. Callable from app.py"""
    print("⏳ [Scheduler] Running Daily Sync...")
    if update_config():
        run_downloader()
    print("✅ [Scheduler] Sync Complete.")

if __name__ == "__main__":
    run_full_sync()
