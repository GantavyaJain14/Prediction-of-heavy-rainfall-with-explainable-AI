
import os
import pandas as pd

# Create directories
dirs = ["app", "src", "data", "models"]
for d in dirs:
    os.makedirs(f"d:/Practice/xai/{d}", exist_ok=True)
    print(f"Created {d}")

# Read Excel
try:
    df = pd.read_excel("d:/Practice/xai/MappingH5IMD.xlsx")
    print("Columns:", df.columns.tolist())
    print("First 5 rows:")
    print(df.head())
except Exception as e:
    print(f"Error reading excel: {e}")
