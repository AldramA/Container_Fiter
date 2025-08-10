class Container:
    """Class representing a container with dimensions and weight limit"""
    
    STANDARD_CONTAINERS = {
        "20ft Standard": {"length": 590, "width": 235, "height": 239, "weight": 28000},
        "40ft Standard": {"length": 1200, "width": 235, "height": 239, "weight": 30000},
        "40ft High Cube": {"length": 1200, "width": 235, "height": 269, "weight": 30000},
    }
    
    def __init__(self, length: float, width: float, height: float, max_weight: float):
        """Initialize container with dimensions and weight limit"""
        if any(dim <= 0 for dim in [length, width, height, max_weight]):
            raise ValueError("All dimensions and max weight must be positive")
            
        self.length = length
        self.width = width
        self.height = height
        self.max_weight = max_weight
        self.volume = length * width * height
        
    @classmethod
    def from_type(cls, container_type: str):
        """Create a container instance from a standard container type"""
        if container_type not in cls.STANDARD_CONTAINERS:
            raise ValueError(f"Unknown container type: {container_type}")
            
        specs = cls.STANDARD_CONTAINERS[container_type]
        return cls(
            length=specs["length"],
            width=specs["width"],
            height=specs["height"],
            max_weight=specs["weight"]
        )
