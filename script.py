import datetime
import pandas as pd
import requests
import io
import os

# Calculate exact Indian Standard Time execution windows
current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
date_str = current_time.strftime("%d%m%Y")
date_iso = current_time.strftime("%Y-%m-%d")

url = f"https://archives.nseindia.com/content/nsccl/fao_participant_oi_{date_str}.csv"

# Emulate structured human traffic metrics
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

master_file = "historical_participant_oi.csv"

try:
    print(f"Attempting to download data from link: {url}")
    response = requests.get(url, headers=headers, timeout=25)
    
    if response.status_code == 200:
        # Load string stream while skipping metadata header row
        df = pd.read_csv(io.StringIO(response.text), skiprows=1)
        
        # Format string elements clean
        df.columns = df.columns.str.strip()
        df['Date'] = date_iso
        
        # Filter matching data boundaries
        required_cols = ['Date', 'Client Type', 'Future Index Long', 'Future Index Short']
        df = df[required_cols]
        df = df[df['Client Type'] != 'TOTAL']
        
        # Append data validation loop
        if not os.path.isfile(master_file):
            df.to_csv(master_file, index=False)
            print("Successfully created a new master file.")
        else:
            existing_df = pd.read_csv(master_file)
            if not ((existing_df['Date'] == date_iso).any()):
                df.to_csv(master_file, mode='a', header=False, index=False)
                print(f"Successfully added tracking metrics for: {date_iso}")
            else:
                print(f"Data values for {date_iso} already logged.")
    else:
        print(f"NSE Server responded with code: {response.status_code}. (Market might be closed or data is unreleased yet).")

except Exception as e:
    print(f"Fatal script execution interruption: {e}")
