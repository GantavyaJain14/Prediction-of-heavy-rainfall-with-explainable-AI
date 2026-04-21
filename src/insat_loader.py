import h5py
import numpy as np
import os

def load_satellite_image(filepath):
    """
    Reads an INSAT .h5 file and returns the IMC (Image) data.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    try:
        with h5py.File(filepath, 'r') as f:
            # Based on inspection, the key is 'IMC'
            if 'IMC' not in f.keys():
                raise ValueError("Invalid H5 file: Missing 'IMC' key")
            
            # The data shape was (1, 2816, 2805). Squeeze to remove the first dim.
            data = np.squeeze(f['IMC'][:])
            
            # Handle missing values (often -999 or NaN)
            data = np.where(data < 0, np.nan, data)
            
            # Robust Normalization (2% - 98%) to fix dark images
            p2 = np.nanpercentile(data, 2)
            p98 = np.nanpercentile(data, 98)
            
            # Clip outliers
            data_clipped = np.clip(data, p2, p98)
            
            if p98 - p2 > 0:
                normalized_data = (data_clipped - p2) / (p98 - p2)
            else:
                normalized_data = np.zeros_like(data)
                
            return normalized_data, data # Return both for plotting and analysis

    except Exception as e:
        print(f"Error loading H5 file: {e}")
        raise e
