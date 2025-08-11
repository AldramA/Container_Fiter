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

    def get_rotations(self):
        """Return a list of all possible rotations for the item"""
        # For simplicity, we consider 3 main rotations (l,w,h), (w,h,l), (h,l,w)
        # In a real-world scenario, more rotations might be considered
        rotations = [
            (self.length, self.width, self.height),
            (self.width, self.height, self.length),
            (self.height, self.length, self.width)
        ]
        return list(set(rotations)) # Use set to remove duplicates

    def rotate(self, rotation_type: int):
        """Rotate the item by swapping its dimensions"""
        if rotation_type == 1: # (l,w,h) -> (w,h,l)
            self.length, self.width, self.height = self.width, self.height, self.length
        elif rotation_type == 2: # (l,w,h) -> (h,l,w)
            self.length, self.width, self.height = self.height, self.length, self.width
        # Default is no rotation
