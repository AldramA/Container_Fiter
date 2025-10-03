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
        """
        Create a more intelligent initial solution using a greedy approach.
        Items are sorted by volume and placed at the best available position.
        """
        # Sort items by volume in descending order
        sorted_items = sorted(items, key=lambda item: item.volume, reverse=True)

        solution = []
        # Keep track of occupied space using a simple list of placed items
        placed_items = []
        
        for item in sorted_items:
            best_pos = None
            min_dist = float('inf')
            
            # Find the best position for the current item
            # We check a set of possible positions (corners of existing items and container)
            possible_positions = self._get_possible_positions(placed_items)
            
            for pos in possible_positions:
                # Create a temporary solution to check for validity
                temp_solution = solution + [(item, pos)]

                if not self._has_overlaps_or_out_of_bounds(temp_solution, check_all=False):
                    # Prefer positions closer to the origin (more compact)
                    dist = np.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2)
                    if dist < min_dist:
                        min_dist = dist
                        best_pos = pos

            if best_pos:
                solution.append((item, best_pos))
                placed_items.append((item, best_pos))

        return solution

    def _get_possible_positions(self, placed_items: List[Tuple[Item, Tuple[float, float, float]]]) -> List[Tuple[float, float, float]]:
        """
        Generate a list of possible positions for a new item.
        These positions are at the corners of already placed items.
        """
        positions = set([(0, 0, 0)])
        for item, pos in placed_items:
            x, y, z = pos
            positions.add((x + item.length, y, z))
            positions.add((x, y + item.width, z))
            positions.add((x, y, z + item.height))
        return list(positions)
    
    def _generate_neighbor(self, solution: List[Tuple[Item, Tuple[float, float, float]]]) -> List[Tuple[Item, Tuple[float, float, float]]]:
        """
        Generate a neighboring solution by performing one of three actions:
        1. Swap two items' positions.
        2. Move an item to a new valid position.
        3. Rotate an item.
        """
        neighbor = solution.copy()
        if not neighbor:
            return neighbor

        # Choose a random action
        action = np.random.choice(['swap', 'move', 'rotate'])

        if action == 'swap' and len(neighbor) >= 2:
            # Swap two random items' positions
            i, j = np.random.choice(len(neighbor), 2, replace=False)
            item_i, pos_i = neighbor[i]
            item_j, pos_j = neighbor[j]
            neighbor[i] = (item_i, pos_j)
            neighbor[j] = (item_j, pos_i)

        elif action == 'move':
            # Move an item to a new valid random position
            idx = np.random.randint(0, len(neighbor))
            item, _ = neighbor.pop(idx)
            
            # Find a new valid position
            placed_items = neighbor
            possible_positions = self._get_possible_positions(placed_items)
            np.random.shuffle(possible_positions)

            new_pos = None
            for pos in possible_positions:
                temp_solution = neighbor + [(item, pos)]
                if not self._has_overlaps_or_out_of_bounds(temp_solution, check_all=False):
                    new_pos = pos
                    break

            if new_pos:
                neighbor.append((item, new_pos))
            else:
                # If no valid position found, revert to original solution
                return solution

        elif action == 'rotate':
            # Rotate a random item
            idx = np.random.randint(0, len(neighbor))
            item, pos = neighbor[idx]

            # Create a copy to avoid modifying the original item in the solution
            rotated_item = Item(item.length, item.width, item.height, item.weight, item.name, item.item_type)

            # Choose a random rotation
            rotation_type = np.random.randint(1, 3)
            rotated_item.rotate(rotation_type)

            # Replace the old item with the rotated one
            neighbor[idx] = (rotated_item, pos)

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
    
    def _has_overlaps_or_out_of_bounds(self, solution: List[Tuple[Item, Tuple[float, float, float]]], check_all: bool = True) -> bool:
        """
        Check if solution has overlapping items or items out of container bounds.
        If check_all is False, only the last item is checked against the others.
        """
        if not solution:
            return False

        if check_all:
            items_to_check = solution
        else:
            # Only check the last item against the rest
            items_to_check = [solution[-1]]

        for i, (item_i, pos_i) in enumerate(items_to_check):
            x1, y1, z1 = pos_i
            
            # Check boundaries
            if (x1 < 0 or x1 + item_i.length > self.container_length or
                y1 < 0 or y1 + item_i.width > self.container_width or
                z1 < 0 or z1 + item_i.height > self.container_height):
                return True
            
            # Check overlaps with other items
            # If checking all, compare with subsequent items.
            # If checking last item, compare with all other items.
            compare_list = solution[i+1:] if check_all else solution[:-1]
            for item_j, pos_j in compare_list:
                x2, y2, z2 = pos_j
                
                if (x1 < x2 + item_j.length and x2 < x1 + item_i.length and
                    y1 < y2 + item_j.width and y2 < y1 + item_i.width and
                    z1 < z2 + item_j.height and z2 < z1 + item_i.height):
                    return True
                    
        return False
