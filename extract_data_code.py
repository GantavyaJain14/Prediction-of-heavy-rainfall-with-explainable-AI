import json
import sys
import os

def extract_data_loading(filepath):
    try:
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return
            
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        print(f"--- Data Loading Code in {os.path.basename(filepath)} ---")
        
        cells = nb.get('cells', [])
        
        code_cells = [c for c in cells if c['cell_type'] == 'code']
        
        found = False
        for i, cell in enumerate(code_cells):
            source = "".join(cell['source'])
            # Look for common data loading keywords
            if any(x in source for x in ['read_excel', 'read_csv', 'h5py', 'load', '.h5', 'xlsx', 'open(']):
                print(f"\n[Cell {i}]")
                print(source[:500]) # First 500 chars
                found = True
        
        if not found:
            print("No obvious data loading code found.")

    except Exception as e:
        print(f"Error reading notebook {filepath}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "d:/Practice/xai/SIH_XAI_IMD_RAINFALL.ipynb"
    
    extract_data_loading(filepath)
