import pandas as pd
import sqlite3
import os

# Configuration
SHEET_ID = "1p4FiH2z5tgr8vlfbg5EE2dZm7g4HHWRr8doBbPzpUrk"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
DB_NAME = "trialhub.db"

def import_data():
    print("Downloading data from Google Sheet...")
    try:
        # Read first few rows to find header
        df_raw = pd.read_csv(CSV_URL, header=None, nrows=20)
        
        # Find header row index
        header_row_idx = None
        for i, row in df_raw.iterrows():
            # Check if row contains 'STT' and 'Ngày Trial' (or similar)
            row_str = row.astype(str).str.cat(sep=' ')
            if 'STT' in row_str and 'Trial' in row_str:
                header_row_idx = i
                break
        
        if header_row_idx is None:
            print("Could not find header row. Defaulting to 0.")
            header_row_idx = 0
        else:
            print(f"Found header at row index: {header_row_idx}")

        # Read full data with correct header
        df = pd.read_csv(CSV_URL, header=header_row_idx)
        print(f"Downloaded {len(df)} rows.")
        
    except Exception as e:
        print(f"Error downloading data: {e}")
        return

    print("Columns found:", df.columns.tolist())

    # Normalize column names
    df.columns = df.columns.str.strip()
    
    # Rename map
    rename_map = {
        'STT': 'stt',
        'Ngày Trial': 'trial_date',
        'Thời gian': 'time',
        'Link Trial': 'meet_link',
        'Môn': 'subject',
        'Số Điện Thoại': 'phone',
        'Tình Trạng': 'status',
        'Note': 'note',
        'Phiếu Đánh Giá': 'evaluator',
        'TVV': 'creator'
    }
    
    # Rename
    df_db = df.rename(columns=rename_map)
    
    # Target columns
    target_cols = ['stt', 'trial_date', 'time', 'meet_link', 'subject', 'phone', 'status', 'note', 'evaluator', 'creator']
    
    # Add missing
    for col in target_cols:
        if col not in df_db.columns:
            df_db[col] = None
            
    df_db = df_db[target_cols]

    # Filter empty
    df_db = df_db.dropna(subset=['stt', 'trial_date'], how='all')
    
    print(f"Rows to insert: {len(df_db)}")

    # Connect to SQLite
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Insert data
    print("Inserting data...")
    
    # Drop table to ensure fresh schema with ID
    cursor.execute("DROP TABLE IF EXISTS trials")
    
    # Create table
    print("Creating table 'trials'...")
    cursor.execute("""
    CREATE TABLE trials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stt TEXT,
        trial_date TEXT,
        time TEXT,
        meet_link TEXT,
        subject TEXT,
        phone TEXT,
        status TEXT,
        note TEXT,
        evaluator TEXT,
        creator TEXT
    )
    """)
    
    try:
        df_db.to_sql('trials', conn, if_exists='append', index=False)
        print("Data imported successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")

    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM trials")
    count = cursor.fetchone()[0]
    print(f"Total rows in database: {count}")
    
    conn.close()

if __name__ == "__main__":
    import_data()






