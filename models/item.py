class Item:
    """Class representing an item to be loaded into the container"""
    
    def __init__(self, length: float, width: float, height: float, 
                 weight: float, name: str = None, item_type: str = None):
        """Initialize an item with dimensions and properties"""
        # Validate dimensions
        if any(dim <= 0 for dim in [length, width, height, weight]):
            raise ValueError("All dimensions and weight must be positive")
            
        self.length = length
        self.width = width
        self.height = height
        self.weight = weight
        self.name = name if name else ""
        self.item_type = item_type
        self.volume = length * width * height
        
    def __str__(self):
        return f"{self.name} ({self.item_type}): {self.length}×{self.width}×{self.height}, {self.weight}kg"
        
    def __repr__(self):
        return self.__str__()
