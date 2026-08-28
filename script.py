import datetime
import pandas as pd
import requests
import io
import os

# 1. Fetch current date in IST timezone
# GitHub Actions runs on UTC, so we shift it to target the current Indian trading day
current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
date_str = current_time.strftime("%d%m%Y")
date_iso = current_time.strftime("%Y-%m-%d")

url = f"https://nseindia.com_{date_str}.csv"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

master_file = "historical_participant_oi.csv"

try:
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code == 200:
        # NSE puts metadata on row 0; dynamic data starts on row 1
        df = pd.read_csv(io.StringIO(response.text), skiprows=1)
        
        # Clean white spaces from columns
        df.columns = df.columns.str.strip()
        df['Date'] = date_iso
        
        # Filter down to the essential Index Futures columns
        required_cols = ['Date', 'Client Type', 'Future Index Long', 'Future Index Short']
        df = df[required_cols]
        
        # Drop the cumulative totals row to preserve raw data clean up
        df = df[df['Client Type'] != 'TOTAL']
        
        # Append data or create the master file if it doesn't exist
        if not os.path.isfile(master_file):
            df.to_csv(master_file, index=False)
        else:
            # Prevent appending identical data duplicates if run twice
            existing_df = pd.read_csv(master_file)
            if not ((existing_df['Date'] == date_iso).any()):
                df.to_csv(master_file, mode='a', header=False, index=False)
                print(f"Data successfully appended for {date_iso}")
            else:
                print(f"Data for {date_iso} already exists in master file.")
    else:
        print(f"No file available on NSE servers. Market may be closed. Status: {response.status_code}")
except Exception as e:
    print(f"Execution Error: {e}")
