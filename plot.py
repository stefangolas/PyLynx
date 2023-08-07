# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 20:19:41 2023

@author: stefa
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from mm4_cmd import xdata, ydata, channel_data
import math

import matplotlib.pyplot as plt

def create_filled_grid(x_values, y_values, output_values):
    # Determine the dimensions of the grid
    unique_x_values = sorted(set(x_values))
    unique_y_values = sorted(set(y_values))
    num_cols = len(unique_x_values)
    num_rows = len(unique_y_values)

    # Create a dictionary to map x values to column indices
    x_to_col = {x: i for i, x in enumerate(unique_x_values)}

    # Create a dictionary to map y values to row indices
    y_to_row = {y: i for i, y in enumerate(unique_y_values)}

    # Create a grid of NaNs to represent the cells
    grid = np.full((num_rows, num_cols), np.nan)

    # Fill in the grid with output values based on x and y coordinates
    for x, y, output in zip(x_values, y_values, output_values):
        col_index = x_to_col[x]
        row_index = y_to_row[y]
        grid[row_index][col_index] = output

    # Plot the filled-in grid
    plt.imshow(grid, cmap='viridis', origin='lower')
    plt.colorbar()
    plt.show()


create_filled_grid(xdata, ydata, channel_data)

