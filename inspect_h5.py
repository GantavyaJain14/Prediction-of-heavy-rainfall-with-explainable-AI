import h5py
import os

def inspect_h5(filename):
    print(f"--- Inspecting {filename} ---")
    try:
        with h5py.File(filename, 'r') as f:
            print("Keys:", list(f.keys()))
            
            # recursive print function
            def print_structure(name, obj):
                if isinstance(obj, h5py.Dataset):
                    print(f"{name}: {obj.shape} ({obj.dtype})")
                elif isinstance(obj, h5py.Group):
                    print(f"{name}/")

            f.visititems(print_structure)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    files = [f for f in os.listdir("d:/Practice/xai") if f.endswith(".h5")]
    for f in files:
        inspect_h5(os.path.join("d:/Practice/xai", f))
