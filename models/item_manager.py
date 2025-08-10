from typing import List, Optional
from .item import Item

class ItemManager:
    """Class to manage items and their unique names"""
    
    def __init__(self):
        self.items: List[Item] = []
        self._type_counters = {}
    
    def generate_unique_name(self, base_name: str, item_type: str) -> str:
        """Generate a unique name for an item"""
        if not item_type:
            raise ValueError("Item type must be specified")
            
        if base_name:
            # If base name provided, ensure it's unique
            counter = 1
            new_name = base_name
            while any(item.name == new_name for item in self.items):
                new_name = f"{base_name}_{counter}"
                counter += 1
            return new_name
        else:
            # Generate type-based name
            if item_type not in self._type_counters:
                self._type_counters[item_type] = 0
            self._type_counters[item_type] += 1
            return f"{item_type}_{self._type_counters[item_type]}"
    
    def add_item(self, length: float, width: float, height: float,
                weight: float, name: str = "", item_type: Optional[str] = None) -> Item:
        """Create and add a new item"""
        # Generate unique name
        final_name = self.generate_unique_name(name, item_type)
        
        # Create new item
        item = Item(length, width, height, weight, final_name, item_type)
        self.items.append(item)
        return item
    
    def remove_item(self, item: Item) -> None:
        """Remove an item from the list"""
        if item in self.items:
            self.items.remove(item)
    
    def clear_items(self) -> None:
        """Clear all items"""
        self.items.clear()
        self._type_counters.clear()
