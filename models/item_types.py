def determine_item_type(length: float, width: float, height: float) -> str:
    """Determine item type based on dimensions"""
    # Sort dimensions
    dims = sorted([length, width, height], reverse=True)
    longest, middle, shortest = dims
    
    # Calculate volume
    volume = length * width * height
    
    if volume > 800000:  # Large volume items
        return 'Pallet'
    elif longest >= 200 and middle >= 100:
        return 'LongBox'
    elif volume > 200000 and shortest >= 60:
        return 'LargeBox'
    elif shortest <= 40 and volume > 50000:
        return 'FlatBox'
    elif volume <= 50000:
        return 'SmallBox'
    elif 50000 < volume <= 150000:
        return 'Carton'
    else:
        return 'StandardBox'
