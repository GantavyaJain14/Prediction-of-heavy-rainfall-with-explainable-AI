import json

def summarize_notebook(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        print(f"--- Summary of {filepath} ---")
        
        cells = nb.get('cells', [])
        print(f"Total Cells: {len(cells)}")
        
        code_cells = [c for c in cells if c['cell_type'] == 'code']
        md_cells = [c for c in cells if c['cell_type'] == 'markdown']
        
        print(f"Code Cells: {len(code_cells)}")
        print(f"Markdown Cells: {len(md_cells)}")
        
        print("\n--- Imports Found ---")
        imports = set()
        for cell in code_cells:
            for line in cell['source']:
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    imports.add(line.strip().split('#')[0].strip())
        for i in sorted(list(imports))[:20]: # Show top 20 imports
            print(i)
            
        print("\n--- Markdown Headers ---")
        for cell in md_cells:
            for line in cell['source']:
                if line.strip().startswith('#'):
                    print(line.strip())

    except Exception as e:
        print(f"Error reading notebook: {e}")

if __name__ == "__main__":
    summarize_notebook("d:/Practice/xai/SIH_XAI_IMD_RAINFALL.ipynb")
