import numpy as np

def predict_impact(raw_data):
    """
    Analyzes the raw satellite data to predict rainfall impact.
    
    Args:
        raw_data (np.array): The raw sensor values (Kelvin or Counts).
        
    Returns:
        dict: Prediction result with status, confidence, and metrics.
    """
    # Filter out NaNs for analysis
    valid_pixels = raw_data[~np.isnan(raw_data)]
    
    if len(valid_pixels) == 0:
        return {
            "status": "No Data",
            "confidence": 0,
            "message": "Image contains no valid data."
        }

    # Heuristic: Lower values in IR usually mean colder cloud tops -> Higher Clouds -> More Rain
    # However, depending on the INSAT product (visible vs IR), it might be inverted.
    # Assuming standard IR where brighter/higher value = colder/higher clouds (or processed counts)
    # Let's derive a simple metric: Percent of pixels above a "Storm Threshold"
    
    # Calculate some stats
    mean_val = np.mean(valid_pixels)
    max_val = np.max(valid_pixels)
    p95 = np.percentile(valid_pixels, 95)
    
    # Define a threshold for "High Impact" (This would be tuned by ML in a real training loop)
    # For now, we use a logic-based threshold relative to the image's dynamic range
    threshold = np.nanpercentile(raw_data, 90) 
    
    # Count pixels above threshold (representing dense clouds)
    storm_pixels = np.sum(raw_data > threshold)
    total_pixels = raw_data.size
    storm_ratio = storm_pixels / total_pixels
    
    # Classification Logic
    if storm_ratio > 0.15:
        status = "High Impact (Heavy Rain)"
        confidence = min(0.98, 0.7 + (storm_ratio * 2)) # Artificial confidence scaling
        message = "Dense cloud formations detected. Potential for heavy downpour."
    elif storm_ratio > 0.05:
        status = "Moderate Rain"
        confidence = 0.85
        message = "Scattered rain clouds detected."
    else:
        status = "Low Chance of Rain"
        confidence = 0.90
        message = "Clear sky or low cloud density."
        
    return {
        "status": status,
        "confidence": round(confidence * 100, 1), # Percentage
        "storm_ratio": round(storm_ratio * 100, 2),
        "message": message,
        "details": {
            "mean_intensity": float(round(mean_val, 2)),
            "max_intensity": float(round(max_val, 2))
        }
    }
