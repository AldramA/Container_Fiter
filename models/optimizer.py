import numpy as np
from typing import List, Tuple
from .item import Item

class ContainerOptimizer:
    """Optimize container loading using Simulated Annealing"""
    
    def __init__(self, container_dims: Tuple[float, float, float], max_weight: float):
        self.container_length = container_dims[0]
        self.container_width = container_dims[1]
        self.container_height = container_dims[2]
        self.max_weight = max_weight
        self.best_solution = None
        self.best_score = float('-inf')
        
    def optimize(self, items: List[Item], initial_temp: float, cooling_rate: float, max_iter: int,
                progress_callback=None) -> Tuple[List[Tuple[Item, Tuple[float, float, float]]], float]:
        """
        Optimize item placement using simulated annealing
        Returns: (item_positions, utilization_score)
        """
        # Initialize positions randomly
        current_solution = self._initialize_solution(items)
        current_score = self._evaluate_solution(current_solution)
        
        self.best_solution = current_solution.copy()
        self.best_score = current_score
        
        temperature = initial_temp
        iteration = 0
        
        while iteration < max_iter and temperature > 0.1:
            # Update progress if callback provided
            if progress_callback:
                progress = (iteration / max_iter) * 100
                progress_callback(progress, f"Iteration {iteration}/{max_iter}")
            
            # Generate neighbor solution
            neighbor = self._generate_neighbor(current_solution)
            neighbor_score = self._evaluate_solution(neighbor)
            
            # Calculate acceptance probability
            delta = neighbor_score - current_score
            if delta > 0 or np.random.random() < np.exp(delta / temperature):
                current_solution = neighbor
                current_score = neighbor_score
                
                # Update best solution if needed
                if current_score > self.best_score:
                    self.best_solution = current_solution.copy()
                    self.best_score = current_score
            
            # Cool down
            temperature *= cooling_rate
            iteration += 1
        
        if progress_callback:
            progress_callback(100, "Optimization complete!")
        
        return self.best_solution, self.best_score
    
    def _initialize_solution(self, items: List[Item]) -> List[Tuple[Item, Tuple[float, float, float]]]:
        """Create initial random solution"""
        solution = []
        available_height = self.container_height
        current_layer_height = 0
        x, y = 0, 0
        
        for item in items:
            # If item doesn't fit in current layer, start new layer
            if y + item.width > self.container_width:
                y = 0
                x += item.length
                if x + item.length > self.container_length:
                    x = 0
                    current_layer_height = available_height - item.height
                    available_height -= item.height
            
            # Add item with its position
            solution.append((item, (x, y, current_layer_height)))
            y += item.width
            
        return solution
    
    def _generate_neighbor(self, solution: List[Tuple[Item, Tuple[float, float, float]]]) -> List[Tuple[Item, Tuple[float, float, float]]]:
        """Generate neighboring solution by swapping two items"""
        neighbor = solution.copy()
        if len(neighbor) < 2:
            return neighbor
            
        # Swap two random items
        i, j = np.random.choice(len(neighbor), 2, replace=False)
        item_i, pos_i = neighbor[i]
        item_j, pos_j = neighbor[j]
        
        neighbor[i] = (item_i, pos_j)
        neighbor[j] = (item_j, pos_i)
        
        return neighbor
    
    def _evaluate_solution(self, solution: List[Tuple[Item, Tuple[float, float, float]]]) -> float:
        """
        Evaluate solution quality
        Returns: score (higher is better)
        """
        if not solution:
            return float('-inf')
        
        # Check volume utilization
        total_volume = sum(item.volume for item, _ in solution)
        container_volume = self.container_length * self.container_width * self.container_height
        volume_utilization = total_volume / container_volume
        
        # Check weight constraint
        total_weight = sum(item.weight for item, _ in solution)
        if total_weight > self.max_weight:
            return float('-inf')
        
        # Check overlaps and boundaries
        if self._has_overlaps_or_out_of_bounds(solution):
            return float('-inf')
        
        # Calculate compactness (prefer items closer to origin)
        positions = np.array([pos for _, pos in solution])
        avg_distance = np.mean(np.sqrt(np.sum(positions**2, axis=1)))
        compactness = 1 / (1 + avg_distance)
        
        # Final score combines utilization and compactness
        return volume_utilization + 0.2 * compactness
    
    def _has_overlaps_or_out_of_bounds(self, solution: List[Tuple[Item, Tuple[float, float, float]]]) -> bool:
        """Check if solution has overlapping items or items out of container bounds"""
        for i, (item_i, pos_i) in enumerate(solution):
            x1, y1, z1 = pos_i
            
            # Check boundaries
            if (x1 < 0 or x1 + item_i.length > self.container_length or
                y1 < 0 or y1 + item_i.width > self.container_width or
                z1 < 0 or z1 + item_i.height > self.container_height):
                return True
            
            # Check overlaps with other items
            for j, (item_j, pos_j) in enumerate(solution[i+1:], i+1):
                x2, y2, z2 = pos_j
                
                if (x1 < x2 + item_j.length and x2 < x1 + item_i.length and
                    y1 < y2 + item_j.width and y2 < y1 + item_i.width and
                    z1 < z2 + item_j.height and z2 < z1 + item_i.height):
                    return True
                    
        return False
