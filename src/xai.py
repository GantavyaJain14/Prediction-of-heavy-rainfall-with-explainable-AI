import numpy as np
import matplotlib
matplotlib.use('Agg') # Fix for running in Flask/Threaded environment
import matplotlib.pyplot as plt
import io
import base64
from matplotlib import cm

def generate_heatmap(normalized_data):
    """
    Generates an XAI heatmap overlaid on the satellite image.
    Returns the image as a base64 string for the web.
    """
    try:
        # Create a figure
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # 1. Plot the base satellite image (Grayscale)
        # Apply Gamma correction to artificially brighten the dark background elements
        masked_data = np.ma.masked_invalid(normalized_data)
        gamma = 0.5 # Brightens the midtones so context (land/ocean) is visible
        enhanced_data = np.power(masked_data, gamma)
        
        # We use a 'terrain' or 'ocean' colormap so the physical ground resembles a map
        # Darker/Warmer areas (0) become blue/green/brown, Colder clouds (1) become white
        ax.imshow(enhanced_data, cmap='terrain', interpolation='nearest') 
        
        ax.set_xlabel("Longitude Index (Pixels)", color='gray')
        ax.set_ylabel("Latitude Index (Pixels)", color='gray')
        
        # 2. Plot the "Activation Map" (XAI)
        # Instead of just a percentile, require a minimum threshold to avoid highlighting clear skies
        # Assuming normalized data 0-1, clouds are towards 1. 0.6 is a decent absolute floor.
        absolute_floor = 0.6
        percentile_threshold = np.nanpercentile(normalized_data, 85)
        final_threshold = max(absolute_floor, percentile_threshold)
        
        mask_indices = normalized_data > final_threshold
        
        # Create a red/orange overlay
        overlay = np.zeros_like(normalized_data)
        overlay[mask_indices] = 1.0
        
        # We use standard 'autumn' colormap but strong solid red looks better
        custom_cmap = matplotlib.colors.ListedColormap(['none', 'red'])
        ax.imshow(mask_indices, cmap=custom_cmap, alpha=0.55)
        
        # Add contours to make the storm cells pop more scientifically
        if np.any(mask_indices):
            ax.contour(normalized_data, levels=[final_threshold], colors=['yellow'], linewidths=0.5, alpha=0.8)
            
        ax.set_title("XAI Physical Explanation: Red / Yellow boundaries = Convective Storm Cores", color='white', pad=10)
        
        # Format the axes for space UI
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#333333')
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1, facecolor='#0b0d17')
        plt.close(fig)
        
        # Encode to Base64
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        return image_base64

    except Exception as e:
        print(f"Error generating XAI: {e}")
        return None
