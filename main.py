#!/usr/bin/env python3
"""
Enhanced Container Loading Optimizer
Advanced 3D container packing optimization with modern GUI
"""

# Standard library imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json
from datetime import datetime
import threading
from typing import List, Tuple, Optional

# Third-party imports
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.colors as mcolors

# Local imports
from models.item_manager import ItemManager
from models.item import Item
from models.item_types import determine_item_type
from models.optimizer import ContainerOptimizer


class ContainerLoadingGUI:
    """Enhanced GUI with modern design and features"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Container Loading Optimizer")
        self.root.geometry("1400x900")
        # Maximize window based on platform
        try:
            self.root.state('zoomed')  # Windows
        except:
            self.root.attributes('-zoomed', True)  # Linux
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Initialize item manager
        self.item_manager = ItemManager()
        self.containers = []
        self.current_figure = None
        self.canvas = None
        self.optimization_thread = None
        self.optimizer = None
        
        # Color scheme for item types
        self.item_colors = {
            'Carton': '#FF6B6B',
            'Pallet': '#4ECDC4',
            'LargeBox': '#45B7D1',
            'FlatBox': '#96CEB4',
            'SmallBox': '#FFEAA7',
            'LongBox': '#DDA0DD',
            'StandardBox': '#FFB6C1',
            'default': '#C0C0C0'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create tabs
        self.setup_input_tab()
        self.setup_visualization_tab()
        self.setup_analysis_tab()

    def setup_input_tab(self):
        """Setup the input and control tab"""
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Input & Control")
        
        # Create paned window for layout
        paned = ttk.PanedWindow(input_frame, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel for inputs
        left_panel = ttk.Frame(paned)
        paned.add(left_panel, weight=1)
        
        # Right panel for items list and controls
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, weight=2)
        
        self.setup_container_settings(left_panel)
        self.setup_item_input(left_panel)
        self.setup_algorithm_settings(left_panel)
        self.setup_items_list(right_panel)
        self.setup_control_buttons(right_panel)

    def setup_container_settings(self, parent):
        """Setup container configuration"""
        frame = ttk.LabelFrame(parent, text="Container Settings", padding="10")
        frame.pack(fill="x", pady=(0, 10))
        
        # Container type selection
        ttk.Label(frame, text="Container Type:").grid(row=0, column=0, sticky="w", pady=2)
        self.container_type = ttk.Combobox(frame, values=["20ft Standard", "40ft Standard", "40ft High Cube", "Custom"], 
                                          state="readonly", width=20)
        self.container_type.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2, padx=(5, 0))
        self.container_type.set("20ft Standard")
        self.container_type.bind('<<ComboboxSelected>>', self.on_container_type_changed)
        
        # Dimensions
        dimensions = [
            ("Length (cm):", "590"),
            ("Width (cm):", "235"),
            ("Height (cm):", "239"),
            ("Max Weight (kg):", "28000")
        ]
        
        self.container_vars = {}
        for i, (label, default) in enumerate(dimensions, 1):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=default)
            self.container_vars[label.split()[0].lower()] = var
            entry = ttk.Entry(frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky="ew", pady=2, padx=(5, 0))
        
        frame.grid_columnconfigure(1, weight=1)

    def setup_item_input(self, parent):
        """Setup item input section"""
        frame = ttk.LabelFrame(parent, text="Add Items", padding="10")
        frame.pack(fill="x", pady=(0, 10))
        
        # Create inner frame for grid layout
        inner_frame = ttk.Frame(frame)
        inner_frame.pack(fill="x", pady=(0, 10))
        
        # Add item button at the top
        ttk.Button(frame, text="➕ Add Item", command=self.add_item).pack(fill="x", pady=(0, 10))
        
        # Item properties
        properties = [
            ("Name:", "", "name"),
            ("Length (cm):", "", "length"),
            ("Width (cm):", "", "width"),
            ("Height (cm):", "", "height"),
            ("Weight (kg):", "", "weight"),
            ("Quantity:", "1", "quantity")
        ]
        
        self.item_vars = {}
        for i, (label, default, key) in enumerate(properties):
            ttk.Label(inner_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar(value=default)
            self.item_vars[key] = var
            entry = ttk.Entry(inner_frame, textvariable=var, width=20)
            entry.grid(row=i, column=1, sticky="ew", pady=2, padx=(5, 0))
        
        # Item type selection
        ttk.Label(inner_frame, text="Type:").grid(row=len(properties), column=0, sticky="w", pady=2)
        self.item_type_var = ttk.Combobox(inner_frame, values=["Auto", "Carton", "Pallet", "LargeBox", 
                                                              "FlatBox", "SmallBox", "LongBox", "StandardBox"], 
                                         state="readonly", width=18)
        self.item_type_var.grid(row=len(properties), column=1, sticky="ew", pady=2, padx=(5, 0))
        self.item_type_var.set("Auto")
        
        # Configure grid column
        inner_frame.grid_columnconfigure(1, weight=1)
        
        frame.grid_columnconfigure(1, weight=1)

    def setup_algorithm_settings(self, parent):
        """Setup algorithm parameters"""
        frame = ttk.LabelFrame(parent, text="Algorithm Settings", padding="10")
        frame.pack(fill="x", pady=(0, 10))
        
        # Initialize algorithm variables
        self.algo_vars = {
            "initial_temperature": tk.StringVar(value="1000"),
            "cooling_rate": tk.StringVar(value="0.95"),
            "max_iterations": tk.StringVar(value="5000")
        }
        
        # Create settings
        settings = [
            ("Initial Temperature:", self.algo_vars["initial_temperature"]),
            ("Cooling Rate:", self.algo_vars["cooling_rate"]),
            ("Max Iterations:", self.algo_vars["max_iterations"])
        ]
        
        for i, (label, var) in enumerate(settings):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            entry = ttk.Entry(frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky="ew", pady=2, padx=(5, 0))
            entry = ttk.Entry(frame, textvariable=var, width=15)
            entry.grid(row=i, column=1, sticky="ew", pady=2, padx=(5, 0))
        
        frame.grid_columnconfigure(1, weight=1)

    def setup_items_list(self, parent):
        """Setup items list display"""
        frame = ttk.LabelFrame(parent, text="Items List", padding="10")
        frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create treeview for items
        columns = ("Name", "Type", "Dimensions", "Weight", "Volume")
        self.items_tree = ttk.Treeview(frame, columns=columns, show="tree headings", height=15)
        
        # Configure columns
        self.items_tree.heading("#0", text="ID", anchor="w")
        self.items_tree.column("#0", width=50, minwidth=50)
        
        for col in columns:
            self.items_tree.heading(col, text=col, anchor="w")
            self.items_tree.column(col, width=100 if col != "Dimensions" else 120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.items_tree.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=self.items_tree.xview)
        self.items_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.items_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def setup_control_buttons(self, parent):
        """Setup control buttons"""
        frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        frame.pack(fill="x")
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(frame, textvariable=self.progress_var).pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(frame, mode='determinate')
        self.progress_bar.pack(fill="x", pady=(5, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x")
        
        self.run_button = ttk.Button(button_frame, text="🚀 Run Optimization", 
                                    command=self.run_optimization)
        self.run_button.pack(side="left", padx=(0, 5))
        
        ttk.Button(button_frame, text="🗑️ Clear All", command=self.clear_all).pack(side="left", padx=(0, 5))
        
        ttk.Button(button_frame, text="💾 Export Results", command=self.export_results).pack(side="right")

    def setup_visualization_tab(self):
        """Setup 3D visualization tab"""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="3D Visualization")
        
        # Create matplotlib figure
        self.current_figure = plt.figure(figsize=(12, 8))
        self.ax = self.current_figure.add_subplot(111, projection='3d')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.current_figure, viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(viz_frame)
        toolbar_frame.pack(fill="x")
        
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()

    def setup_analysis_tab(self):
        """Setup analysis and statistics tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Analysis & Statistics")
        
        # Create text widget for analysis
        self.analysis_text = tk.Text(analysis_frame, wrap="word", font=("Consolas", 11))
        analysis_scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=analysis_scrollbar.set)
        
        self.analysis_text.pack(side="left", fill="both", expand=True)
        analysis_scrollbar.pack(side="right", fill="y")

    def clear_all(self):
        """Clear all data"""
        self.item_manager.clear_items()
        self.update_items_display()
        messagebox.showinfo("Success", "All items cleared!")

    def export_results(self):
        """Export results to file"""
        messagebox.showinfo("Export", "Export functionality will be implemented soon!")

    def run_optimization(self):
        """Run the optimization algorithm"""
        if not self.item_manager.items:
            messagebox.showerror("Error", "No items to optimize! Please add some items first.")
            return
            
        try:
            # Get container dimensions
            length = float(self.container_vars["length"].get())
            width = float(self.container_vars["width"].get())
            height = float(self.container_vars["height"].get())
            max_weight = float(self.container_vars["max"].get())
            
            # Get algorithm parameters
            initial_temp = float(self.algo_vars["initial_temperature"].get())
            cooling_rate = float(self.algo_vars["cooling_rate"].get())
            max_iter = int(self.algo_vars["max_iterations"].get())
            
            # Create optimizer
            self.optimizer = ContainerOptimizer((length, width, height), max_weight)
            
            # Disable run button during optimization
            self.run_button.configure(state="disabled")
            self.progress_var.set("Starting optimization...")
            self.progress_bar["value"] = 0
            
            def progress_callback(progress, message):
                self.progress_bar["value"] = progress
                self.progress_var.set(message)
                self.root.update_idletasks()
            
            # Run optimization in a separate thread
            def optimize_thread():
                try:
                    solution, score = self.optimizer.optimize(
                        self.item_manager.items,
                        initial_temp,
                        cooling_rate,
                        max_iter,
                        progress_callback
                    )
                    
                    # Update visualization in main thread
                    self.root.after(0, lambda: self.update_visualization(solution, score))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Optimization failed: {str(e)}"))
                finally:
                    self.root.after(0, lambda: self.run_button.configure(state="normal"))
            
            # Start optimization thread
            self.optimization_thread = threading.Thread(target=optimize_thread)
            self.optimization_thread.daemon = True
            self.optimization_thread.start()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid parameter values: {str(e)}")
            self.run_button.configure(state="normal")

    def update_items_display(self):
        """Update the items list display"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Add items to tree
        for i, item in enumerate(self.item_manager.items):
            values = (
                item.name,
                item.item_type,
                f"{item.length}×{item.width}×{item.height}",
                f"{item.weight:.1f} kg",
                f"{item.volume:.0f} cm³"
            )
            self.items_tree.insert("", "end", iid=i, text=str(i+1), values=values)
            
    def add_item(self):
        """Add a new item to the list"""
        try:
            # Get values from input fields
            name = self.item_vars["name"].get().strip()
            
            # Convert string values to numbers and validate
            try:
                length = float(self.item_vars["length"].get() or "0")
                width = float(self.item_vars["width"].get() or "0")
                height = float(self.item_vars["height"].get() or "0")
                weight = float(self.item_vars["weight"].get() or "0")
                quantity = int(self.item_vars["quantity"].get() or "0")
            except ValueError:
                raise ValueError("Please enter valid numbers for dimensions, weight, and quantity")
                
            item_type = self.item_type_var.get()
            if item_type == "Auto":
                # Determine type based on dimensions
                item_type = determine_item_type(length, width, height)
            
            # Validate inputs
            if length <= 0 or width <= 0 or height <= 0:
                raise ValueError("Dimensions must be positive numbers")
            if weight <= 0:
                raise ValueError("Weight must be positive")
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            # Create and add items
            for _ in range(quantity):
                # Use ItemManager's add_item which handles name generation
                item = self.item_manager.add_item(length, width, height, weight, 
                                                name=name, item_type=item_type)
            
            # Clear input fields
            for var in self.item_vars.values():
                var.set("")
            self.item_vars["quantity"].set("1")
            
            # Update display
            self.update_items_display()
            messagebox.showinfo("Success", f"{quantity} item(s) added successfully!")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            
    def on_container_type_changed(self, event=None):
        """Handle container type selection change"""
        container_type = self.container_type.get()
        
        # Default dimensions for standard containers
        dimensions = {
            "20ft Standard": (590, 235, 239, 28000),
            "40ft Standard": (1203, 235, 239, 26500),
            "40ft High Cube": (1203, 235, 270, 26500),
        }
        
        if container_type != "Custom":
            length, width, height, weight = dimensions[container_type]
            self.container_vars["length"].set(str(length))
            self.container_vars["width"].set(str(width))
            self.container_vars["height"].set(str(height))
            self.container_vars["max"].set(str(weight))
            
    def update_visualization(self, solution, score):
        """Update 3D visualization with optimization results"""
        # Clear current plot
        self.ax.clear()
        
        # Get container dimensions
        length = float(self.container_vars["length"].get())
        width = float(self.container_vars["width"].get())
        height = float(self.container_vars["height"].get())
        
        # Plot container with thickness
        wall_thickness = 5 # in cm
        
        # Floor with grid pattern
        xx, yy = np.meshgrid(np.arange(0, length, 50), np.arange(0, width, 50))
        self.ax.plot_wireframe(xx, yy, np.full_like(xx, 0), color="peru", alpha=0.5)

        # Walls (outer and inner surfaces)
        # Back wall
        xx, zz = np.meshgrid([0, length], [0, height])
        self.ax.plot_surface(xx, np.full_like(xx, 0), zz, color="gray", alpha=0.3)
        self.ax.plot_surface(xx, np.full_like(xx, wall_thickness), zz, color="darkgray", alpha=0.3)
        # Front wall (door) - omitted for visibility

        # Left wall
        yy, zz = np.meshgrid([0, width], [0, height])
        self.ax.plot_surface(np.full_like(yy, 0), yy, zz, color="gray", alpha=0.3)
        self.ax.plot_surface(np.full_like(yy, wall_thickness), yy, zz, color="darkgray", alpha=0.3)

        # Right wall
        self.ax.plot_surface(np.full_like(yy, length), yy, zz, color="gray", alpha=0.3)
        self.ax.plot_surface(np.full_like(yy, length - wall_thickness), yy, zz, color="darkgray", alpha=0.3)

        # Store artists for picking
        self.plotted_items = []

        # Plot each item
        for item, pos in solution:
            x, y, z = pos
            dx, dy, dz = item.length, item.width, item.height
            
            # Get color based on item type
            color = self.item_colors.get(item.item_type, self.item_colors['default'])
            
            # Create box vertices
            xx = np.array([[x, x+dx, x+dx, x],
                          [x, x+dx, x+dx, x]])
            yy = np.array([[y, y, y+dy, y+dy],
                          [y, y, y+dy, y+dy]])
            zz = np.array([[z, z, z, z],
                          [z+dz, z+dz, z+dz, z+dz]])
            
            # Plot faces with edges and lighting
            light = mcolors.LightSource(azdeg=225, altdeg=10)
            rgb = mcolors.to_rgba(color, alpha=None)
            facecolors = light.shade(rgb, np.full(xx.shape, 1.0))

            surface = self.ax.plot_surface(xx, yy, zz, facecolors=facecolors,
                                 edgecolor='black', linewidth=0.5, alpha=0.8, picker=True)
            self.plotted_items.append((surface, item))

            # Add text label with background for better readability
            self.ax.text(x+dx/2, y+dy/2, z+dz/2, item.name,
                        horizontalalignment='center',
                        verticalalignment='center',
                        bbox=dict(facecolor='white', alpha=0.5, boxstyle='round,pad=0.2'))
        
        # Set labels and title
        self.ax.set_xlabel('Length (cm)')
        self.ax.set_ylabel('Width (cm)')
        self.ax.set_zlabel('Height (cm)')
        utilization = score * 100
        self.ax.set_title(f'Container Loading Solution\nVolume Utilization: {utilization:.1f}%')
        
        # Set axis limits and aspect ratio
        self.ax.set_xlim([0, length])
        self.ax.set_ylim([0, width])
        self.ax.set_zlim([0, height])
        self.ax.set_box_aspect([length, width, height]) # Ensure correct proportions
        
        # Update analysis text
        self.update_analysis(solution, score)
        
        # Switch to visualization tab
        self.notebook.select(1)
        
        # Connect pick event
        self.canvas.mpl_connect('pick_event', self.on_pick)

        # Redraw canvas
        self.canvas.draw()
        
    def on_pick(self, event):
        """Handle item picking in the 3D plot"""
        # Find which item was picked
        for artist, item in self.plotted_items:
            if artist == event.artist:
                # Display item info
                info = (f"Item: {item.name}\n"
                        f"Type: {item.item_type}\n"
                        f"Dimensions: {item.length}×{item.width}×{item.height} cm\n"
                        f"Weight: {item.weight:.1f} kg")
                messagebox.showinfo("Item Details", info)
                return

    def update_analysis(self, solution, score):
        """Update analysis tab with optimization results"""
        self.analysis_text.delete(1.0, tk.END)
        
        # Calculate statistics
        total_items = len(solution)
        total_volume = sum(item.volume for item, _ in solution)
        total_weight = sum(item.weight for item, _ in solution)
        container_volume = (float(self.container_vars["length"].get()) *
                          float(self.container_vars["width"].get()) *
                          float(self.container_vars["height"].get()))
        volume_utilization = (total_volume / container_volume) * 100
        weight_utilization = (total_weight / float(self.container_vars["max"].get())) * 100
        
        # Group items by type
        type_counts = {}
        for item, _ in solution:
            type_counts[item.item_type] = type_counts.get(item.item_type, 0) + 1
        
        # Create analysis report
        report = [
            "🎯 Optimization Results",
            "=" * 40,
            f"Total Items Packed: {total_items}",
            f"Volume Utilization: {volume_utilization:.1f}%",
            f"Weight Utilization: {weight_utilization:.1f}%",
            f"Optimization Score: {score:.4f}",
            "",
            "📦 Items by Type:",
            "=" * 40
        ]
        
        for item_type, count in type_counts.items():
            report.append(f"{item_type}: {count}")
            
        report.extend([
            "",
            "📊 Detailed Statistics:",
            "=" * 40,
            f"Total Volume: {total_volume:.0f} cm³",
            f"Total Weight: {total_weight:.1f} kg",
            f"Container Volume: {container_volume:.0f} cm³",
            f"Max Weight: {self.container_vars['max'].get()} kg"
        ])
        
        # Update text widget
        self.analysis_text.insert(tk.END, "\n".join(report))


if __name__ == "__main__":
    root = tk.Tk()
    app = ContainerLoadingGUI(root)
    root.mainloop()
