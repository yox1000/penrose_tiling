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
labeled_vertices = []  # Track which vertices have been labeled
current_vertex_index = 0

# Initialize Plot
fig, ax = plt.subplots()

# Step 1: Initialize the vertices for the TKR tile and label them on the chart
def initialize_tkr_vertices(position=(0, 0)):
    global current_vertex_index, vertices_table
    # Define the four vertices based on TKR geometry
    p0 = np.array(position)
    p1 = p0 + np.array([1, 0])
    p2 = p1 + np.array([np.cos(-angle_72), np.sin(-angle_72)])
    p3 = p2 + np.array([np.cos(-angle_72 - angle_108), np.sin(-angle_72 - angle_108)])
    
    # Store vertices in `vertices_table` with labels
    vertices = [p0, p1, p2, p3]
    vertices_indices = []
    for vertex in vertices:
        vertices_table[current_vertex_index] = vertex
        ax.plot(vertex[0], vertex[1], 'o', color='blue')
        
        # Offset label slightly to avoid overlap with the vertex itself
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
    polygon_vertices = [vertices_table[idx] for idx in vertices_indices]
    for i in range(len(vertices_indices)):
        start_vertex = vertices_table[vertices_indices[i]]
        end_vertex = vertices_table[vertices_indices[(i + 1) % len(vertices_indices)]]
        ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='black')

    # Fill the TKR tile with light blue
    polygon = Polygon(polygon_vertices, closed=True, color='lightblue', alpha=0.5)
    ax.add_patch(polygon)

# Step 3: Display vertices in a separate table window
# Initialize a variable to hold the table window
table_window = None

def display_vertices_table():
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

# Function to find the closest labeled vertex to the origin
def find_closest_labeled_vertex():
    """
    Finds the closest labeled vertex to the origin (0, 0).
    """
    origin = np.array([0, 0])
    closest_vertex = None
    closest_distance = float('inf')
    
    for idx in labeled_vertices:
        vertex_position = vertices_table[idx]
        distance = np.linalg.norm(vertex_position - origin)
        if distance < closest_distance:
            closest_distance = distance
            closest_vertex = idx

    return closest_vertex

# Function to generate a new TKR tile around the specified vertex
def generate_tkr_around_vertex(vertex_index):
    """
    Generates a new TKR tile using the specified vertex as a starting point
    and labels new vertices clockwise.
    This version ensures the new tile shares vertices with the existing tile.
    """
    global current_vertex_index, labeled_vertices
    base_vertex = vertices_table[vertex_index]
    
    # Create offsets to find the next tile position
    offsets = [
        np.array([np.cos(angle_72), np.sin(angle_72)]),  # Right
        np.array([np.cos(-angle_72), np.sin(-angle_72)]),  # Left
        np.array([np.cos(angle_72 + angle_108), np.sin(angle_72 + angle_108)])  # Up
    ]
    
    # Loop through offsets to find a valid new position
    for offset in offsets:
        new_position = base_vertex + offset  # Calculate new position
        
        # Initialize new vertices and draw the tile
        new_vertices_indices = initialize_tkr_vertices(new_position)
        
        # Label new vertices if not already labeled
        for idx in new_vertices_indices:
            if idx not in labeled_vertices:
                labeled_vertices.append(idx)
        
        draw_tkr_tile(new_vertices_indices)  # Ensure the new tile is drawn
        break  # Stop after placing one tile adjacent

# Modify the button click handler to ensure 5 tiles are generated correctly
def on_button_click(event):
    """
    Handles button click to generate TKR tiles until 5 are created.
    """
    ax.clear()  # Clear plot for each update
    if len(labeled_vertices) < 5:
        # Draw the first TKR tile if not already drawn
        if len(labeled_vertices) == 0:
            vertices_indices = initialize_tkr_vertices()
            draw_tkr_tile(vertices_indices)
            labeled_vertices.extend(vertices_indices)  # Mark first set of vertices as labeled
        else:
            # Find the closest labeled vertex to the origin
            closest_vertex = find_closest_labeled_vertex()
            generate_tkr_around_vertex(closest_vertex)
        
        display_vertices_table()  # Ensure the table is displayed after each tile generation
        
    fig.canvas.draw()  # Refresh plot to display updates

# Set up initial tile and button interaction
def on_button_click(event):
    """
    Handles button click to generate TKR tiles until 5 are created.
    """
    ax.clear()  # Clear plot for each update
    if len(labeled_vertices) < 5:
        # Draw the first TKR tile if not already drawn
        if len(labeled_vertices) == 0:
            vertices_indices = initialize_tkr_vertices()
            draw_tkr_tile(vertices_indices)
            labeled_vertices.extend(vertices_indices)  # Mark first set of vertices as labeled
        else:
            # Find the closest labeled vertex to the origin
            closest_vertex = find_closest_labeled_vertex()
            generate_tkr_around_vertex(closest_vertex)
        
        display_vertices_table()  # Ensure the table is displayed after each tile generation
        
    fig.canvas.draw()  # Refresh plot to display updates

# Button setup
from matplotlib.widgets import Button
ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Add TKR Tile')
button.on_clicked(on_button_click)

plt.show()  # Display main plot window
