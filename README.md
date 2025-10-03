# 3D Container Loading Optimizer

This project is a sophisticated 3D container loading optimizer with a modern graphical user interface (GUI) built using Python's Tkinter library. It provides an efficient solution for the complex problem of packing items of various sizes into a container to maximize space utilization. The application employs a Simulated Annealing algorithm to find a near-optimal packing configuration.

## Features

- **Interactive 3D Visualization**: View the container and the packed items in a 3D space, powered by Matplotlib.
- **Advanced Optimization Algorithm**: Utilizes a Simulated Annealing algorithm to find high-quality solutions to the packing problem.
- **Customizable Inputs**:
    - Choose from standard container types (20ft, 40ft, 40ft High Cube) or define custom container dimensions.
    - Add items with specific dimensions (length, width, height), weight, and quantity.
    - Automatic item type detection based on dimensions.
- **Detailed Analysis**: Get a comprehensive report of the optimization results, including volume and weight utilization, a list of packed items, and more.
- **User-Friendly Interface**: A clean and modern GUI with separate tabs for input, 3D visualization, and analysis.
- **Exportable Results**: (Coming Soon) Functionality to export the packing solution to various formats.

## How to Run

1.  **Prerequisites**:
    - Python 3.6+
    - The following Python libraries:
        - `numpy`
        - `matplotlib`

2.  **Installation**:
    You can install the required libraries using pip:
    ```bash
    pip install numpy matplotlib
    ```

3.  **Running the Application**:
    Execute the `main.py` script to launch the application:
    ```bash
    python main.py
    ```

## The Optimization Algorithm

The core of this application is the `ContainerOptimizer`, which uses a **Simulated Annealing (SA)** metaheuristic to solve the 3D packing problem. Here's a brief overview of how it works:

1.  **Initial Solution**: The algorithm starts by creating a greedy initial solution. It sorts the items by volume and places them one by one in the best available position inside the container.

2.  **Neighbor Generation**: In each iteration, the algorithm generates a "neighbor" solution by making a small, random change to the current solution. The possible changes include:
    - **Swapping** the positions of two items.
    - **Moving** an item to a new valid position.
    - **Rotating** an item to a different orientation.

3.  **Acceptance Criteria**: A new solution is always accepted if it's better than the current one. However, to avoid getting stuck in local optima, it also accepts worse solutions with a certain probability, which is controlled by the "temperature" parameter of the SA algorithm. The temperature decreases over time, making it less likely to accept worse solutions as the algorithm progresses.

4.  **Termination**: The algorithm stops when it reaches a maximum number of iterations or when the temperature drops below a certain threshold. The best solution found during the process is then returned.

This approach allows the optimizer to explore a wide range of possible configurations and find a high-density packing solution in a reasonable amount of time.
