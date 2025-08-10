from typing import Optional

class Item:
    """Enhanced Item class with improved type detection"""
    
    def __init__(self, length: float, width: float, height: float, weight: float, 
                 name: Optional[str] = None, item_type: Optional[str] = None):
        try:
            # Validate and convert dimensions
            if any(not isinstance(x, (int, float)) for x in [length, width, height, weight]):
                raise ValueError("All dimensions and weight must be numbers")
            
            # Convert and store dimensions
            self.length = float(length)
            self.width = float(width)
            self.height = float(height)
            self.weight = float(weight)
            
            # Validate positive values
            if any(x <= 0 for x in [self.length, self.width, self.height, self.weight]):
                raise ValueError("All dimensions and weight must be positive")
            
            # Calculate basic properties
            self.volume = self.length * self.width * self.height
            self.density = self.weight / self.volume
            
            # Handle type assignment
            self.item_type = str(item_type) if item_type and item_type != "Auto" else self._determine_type()
            
            # Handle name assignment (must come after type is determined)
            self.name = str(name) if name else f"{self.item_type}_{id(self)}"
            
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid item parameters: {str(e)}")
    
    def _determine_type(self) -> str:
        """Determine item type based on dimensions"""
        # Sort dimensions
        dims = sorted([self.length, self.width, self.height], reverse=True)
        longest, middle, shortest = dims
        
        # Volume-based classification
        if self.volume > 800000:  # Large volume items
            return 'Pallet'
        elif longest >= 200 and middle >= 100:
            return 'LongBox'
        elif self.volume > 200000 and shortest >= 60:
            return 'LargeBox'
        elif shortest <= 40 and self.volume > 50000:
            return 'FlatBox'
        elif self.volume <= 50000:
            return 'SmallBox'
        elif 50000 < self.volume <= 150000:
            return 'Carton'
        else:
            return 'StandardBox'
            
    def __str__(self) -> str:
        """String representation of the item"""
        return f"{self.name} ({self.item_type}): {self.length}×{self.width}×{self.height}cm, {self.weight}kg"
