import pandas as pd
import os
import glob

def check_mapping():
    # Find the mapping file (handling the (1) suffix)
    files = glob.glob("d:/Practice/xai/datasets/MappingH5IMD*.xlsx")
    if not files:
        print("Mapping file not found!")
        return

    fpath = files[0]
    print(f"Reading: {fpath}")
    
    try:
        df = pd.read_excel(fpath)
        print("Columns:", df.columns.tolist())
        print(df.head())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_mapping()
