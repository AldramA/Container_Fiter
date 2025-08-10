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
