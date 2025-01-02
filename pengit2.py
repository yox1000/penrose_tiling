import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.patches import Polygon

# Constants for angles
angle_72 = np.radians(72)
angle_108 = np.radians(108)

# Dictionary to store vertex positions with their indices
vertices_table = {}
current_vertex_index = 0

# Initialize Plot
fig, ax = plt.subplots()

# Step 1: Initialize the vertices for the TKR tile and label them on the chart
def initialize_tkr_vertices(position=(0, 0)):
    """
    Initializes the vertices for the TKR tile, stores them in `vertices_table`, 
    and labels each vertex on the chart with a small offset for visibility.
    """
    global current_vertex_index, vertices_table
    # Define the four vertices based on TKR geometry
    p0 = np.array(position)
    p1 = p0 + np.array([1, 0])
    p2 = p1 + np.array([np.cos(-angle_72), np.sin(-angle_72)])
    p3 = p2 + np.array([np.cos(-angle_72 - angle_108), np.sin(-angle_72 - angle_108)])
    
    # Store vertices in `vertices_table` and add labels to the chart
    vertices = [p0, p1, p2, p3]
    vertices_indices = []
    for vertex in vertices:
        vertices_table[current_vertex_index] = vertex
        ax.plot(vertex[0], vertex[1], 'o', color='blue')
        
        # Offset label slightly to avoid overlap with the TKR fill color
        offset_x, offset_y = 0.05, 0.05
        ax.text(vertex[0] + offset_x, vertex[1] + offset_y, 
                f'{current_vertex_index}', ha='center', va='center', 
                fontsize=9, color='blue')
        
        vertices_indices.append(current_vertex_index)
        current_vertex_index += 1

    # Ensure the axes have equal scaling
    ax.set_aspect('equal', 'box')
    
    return vertices_indices

# Step 2: Draw edges of the TKR tile by connecting vertices in sequence and fill the tile
def draw_tkr_tile(vertices_indices):
    """
    Draws the edges of the TKR tile by connecting vertices and fills the tile with a light color.
    """
    polygon_vertices = [vertices_table[idx] for idx in vertices_indices]
    for i in range(len(vertices_indices)):
        start_vertex = vertices_table[vertices_indices[i]]
        end_vertex = vertices_table[vertices_indices[(i + 1) % len(vertices_indices)]]
        ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='black')

    # Fill the TKR tile with light blue color
    polygon = Polygon(polygon_vertices, closed=True, color='lightblue', alpha=0.5)
    ax.add_patch(polygon)

# Step 3: Display vertices in a separate table window
table_window = None  # Initialize a variable to hold the table window

def display_vertices_table():
    """
    Displays the vertices and their coordinates in a separate Tkinter window.
    Refreshes the table window if it already exists.
    """
    global table_window
    
    # Check if the table window exists; if so, clear and update it
    if table_window and tk.Toplevel.winfo_exists(table_window):
        for widget in table_window.winfo_children():
            widget.destroy()  # Clear existing table data
    else:
        # Create a new table window if it doesn’t exist
        table_window = tk.Toplevel()
        table_window.title("Vertices Table")

    # Set up a table using Tkinter Treeview
    columns = ('Index', 'X', 'Y')
    tree = ttk.Treeview(table_window, columns=columns, show='headings')
    tree.heading('Index', text='Index')
    tree.heading('X', text='X')
    tree.heading('Y', text='Y')

    # Insert vertex data into the table
    for index, vertex in vertices_table.items():
        tree.insert('', tk.END, values=(index, round(vertex[0], 2), round(vertex[1], 2)))

    # Pack the table into the window
    tree.pack()
    table_window.update_idletasks()

# Set up initial tile and button interaction
def on_button_click(event):
    """
    Handles button click to add a TKR tile, refreshes plot, and displays the vertices table.
    """
    ax.clear()  # Clear plot for each update
    vertices_indices = initialize_tkr_vertices()  # Get the list of initialized vertices
    draw_tkr_tile(vertices_indices)  # Draw edges and fill the TKR tile
    fig.canvas.draw()  # Refresh plot to display updates
    display_vertices_table()  # Display the vertices table

# Button setup
from matplotlib.widgets import Button
ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Add TKR Tile')
button.on_clicked(on_button_click)

plt.show()  # Display main plot window
