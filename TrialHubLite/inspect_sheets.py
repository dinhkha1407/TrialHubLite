import pandas as pd
import io
import requests

SHEET_ID = "1p4FiH2z5tgr8vlfbg5EE2dZm7g4HHWRr8doBbPzpUrk"
XLSX_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"

def inspect():
    print("Downloading XLSX...")
    try:
        response = requests.get(XLSX_URL)
        response.raise_for_status()
        
        print("Reading Excel file...")
        xls = pd.ExcelFile(io.BytesIO(response.content))
        
        print("Sheet names:", xls.sheet_names)
        
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            print(f"Sheet '{sheet}': {len(df)} rows, {len(df.columns)} columns")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
