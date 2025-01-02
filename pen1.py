import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.patches import Polygon
from matplotlib.widgets import Button
import math

# Constants for angles (in radians)
angle_36 = np.radians(36)
angle_72 = np.radians(72)
angle_108 = np.radians(108)
angle_144 = np.radians(144)

# Global variables
vertices_table = {}
current_vertex_index = 0
tiles = []  # Store tile information (vertices, type)
rotation_state = 0  # Track the overall tiling progress
retired_vertices = {0: 0}  # Initialize with vertex 0 retired
vertex_connections = {}
table_window = None

# Initialize Plot
fig, ax = plt.subplots(figsize=(8, 8))  #Removed redundant call from inside on_button_click
ax.set_aspect('equal')  # Ensure equal aspect ratio

# Rotate a point
def rotate_point(point, angle, origin=(0, 0)):
    ox, oy = origin
    px, py = point
    cos_theta, sin_theta = np.cos(angle), np.sin(angle)
    qx = ox + cos_theta * (px - ox) - sin_theta * (py - oy)
    qy = oy + sin_theta * (px - ox) + cos_theta * (py - oy)
    return np.array([qx, qy])

# Check for existing vertex
def find_vertex(vertex, tolerance=1e-6):
    for index, existing_vertex in vertices_table.items():
        if np.allclose(vertex, existing_vertex[:2], atol=tolerance):
            return index
    return None

# Initialize vertices for TKR tile with angle tracking
def initialize_tkr_vertices(position=(0, 0), rotation_angle=0):
    global current_vertex_index, vertices_table
    
    vertices_indices = []
    p0 = np.array(position)
    p1 = p0 + np.array([1, 0])
    p2 = p1 + np.array([np.cos(-angle_72), np.sin(-angle_72)])
    p3 = p2 + np.array([np.cos(-angle_72 - angle_108), np.sin(-angle_72 - angle_108)])
    vertices = [rotate_point(p, rotation_angle) for p in [p0, p1, p2, p3]]
    
    for vertex in vertices:
        vertex_index = find_vertex(vertex)
        if vertex_index is None:
            # Initialize vertex with an angle tracker starting at 0
            vertices_table[current_vertex_index] = (vertex[0], vertex[1], "Active", 0)
            vertex_index = current_vertex_index
            ax.plot(vertex[0], vertex[1], 'o', color='blue')
            ax.text(vertex[0] + 0.05, vertex[1] + 0.05, f'{vertex_index}', ha='center', va='center', fontsize=9, color='blue')
            current_vertex_index += 1
        vertices_indices.append(vertex_index)
    
    ax.set_aspect('equal', 'box')
    return vertices_indices

# Single draw_tile function with color
def draw_tile(vertices_indices, color='lightblue'):
    polygon_vertices = [vertices_table[idx][:2] for idx in vertices_indices]
    for i in range(len(vertices_indices)):
        start_vertex = vertices_table[vertices_indices[i]][:2]
        end_vertex = vertices_table[vertices_indices[(i + 1) % len(vertices_indices)]][:2]
        ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='black')
    polygon = Polygon(polygon_vertices, closed=True, color=color, alpha=0.5)
    ax.add_patch(polygon)

# Update: Refined TNR tile placement logic
def place_tnr_tile():
    """Generate a TNR tile by finding the lowest available vertex and connecting it to form a new thin rhombus tile."""
    global current_vertex_index, vertices_table
    vertices_indices = []

    # Identify the next available starting vertex and its first connected vertex
    for vertex in sorted(vertices_table):
        if vertex not in retired_vertices:
            start_vertex = vertex
            break

    # Determine the next connected vertex to form the TNR tile side
    connected_vertex = start_vertex + 1  # Simplification to select the next vertex; adjust as needed
    
    # Define vertices of TNR tile using specified angles
    p0 = np.array(vertices_table[start_vertex][:2])  # Start at selected vertex
    p1 = np.array(vertices_table[connected_vertex][:2])
    p2 = rotate_point(p1, angle_144, origin=p0)  # Determine third point based on angle

    vertices = [p0, p1, p2]
    for vertex in vertices:
        vertex_index = find_vertex(vertex)
        if vertex_index is None:
            vertices_table[current_vertex_index] = (vertex[0], vertex[1], "Active")
            vertex_index = current_vertex_index
            ax.plot(vertex[0], vertex[1], 'o', color='blue')
            ax.text(vertex[0] + 0.05, vertex[1] + 0.05, f'{vertex_index}', ha='center', va='center', fontsize=9, color='blue')
            current_vertex_index += 1
        vertices_indices.append(vertex_index)

    ax.set_aspect('equal', 'box')
    return vertices_indices

# Update: Check and retire the vertex after a complete rotation
def check_and_retire_vertex(vertex_index):
    """Retires a vertex if it completes a full 360-degree placement (5 connections)."""
    if vertex_connections.get(vertex_index, 0) >= 5 and vertex_index not in retired_vertices:
        retired_vertices.add(vertex_index)
        vertices_table[vertex_index] = (*vertices_table[vertex_index][:2], "Retired")
        print(f"Vertex {vertex_index} is now retired.")

    # Specifically retire vertex 0 after five tiles
    if vertex_index == 0 and rotation_index >= 5:
        retired_vertices.add(0)
        vertices_table[0] = (*vertices_table[0][:2], "Retired")
        print("Vertex 0 is now retired after five TKR tiles.")

# Display vertices in a table
def display_vertices_table():
    global table_window
    if table_window and tk.Toplevel.winfo_exists(table_window):
        for widget in table_window.winfo_children():
            widget.destroy()
    else:
        table_window = tk.Toplevel()
        table_window.title("Vertices Table")

    columns = ('Index', 'X', 'Y', 'Status')
    tree = ttk.Treeview(table_window, columns=columns, show='headings', height=15)
    tree.heading('Index', text='Index')
    tree.heading('X', text='X')
    tree.heading('Y', text='Y')
    tree.heading('Status', text='Status')
    
    for index, (x, y, status) in vertices_table.items():
        tree.insert('', tk.END, values=(index, round(x, 2), round(y, 2), status))
    
    scrollbar = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    tree.pack(side="left", fill="both", expand=True)
    table_window.update_idletasks()

# Move update_tiled_angle function above on_button_click
def update_tiled_angle(vertices_indices, tile_type):
    """Updates the angle coverage around vertices and retires them if they reach 360 degrees."""
    for vertex_index in vertices_indices:
        x, y, status, angle = vertices_table[vertex_index]
        
        # Determine angle increment based on tile type
        angle_increment = 72 if tile_type == 'TKR' else 144 if tile_type == 'TNR' else 0
        
        # Update the tiled angle
        new_angle = angle + angle_increment
        vertices_table[vertex_index] = (x, y, status, new_angle)
        
        # Check if vertex should be retired
        if new_angle >= 360:
            vertices_table[vertex_index] = (x, y, "Retired", new_angle)
            retired_vertices.add(vertex_index)
            print(f"Vertex {vertex_index} has retired after reaching 360 degrees.")

    # Retire all vertices that completed rotation
    for vertex_index in vertices_indices:
        check_and_retire_vertex(vertex_index)

    fig.canvas.draw()
    display_vertices_table()
    global rotation_index  # Add global keyword
    rotation_index += 1

# Move find_next_available_vertex function above on_button_click
def find_next_available_vertex():
    """Finds the lowest indexed vertex that is not retired."""
    for index in range(len(vertices_table)):
        if index not in retired_vertices:
            return index  # Return the first non-retired vertex found
    return None  # Return None if all vertices are retired

# Update: Button click handler to manage retiring and plot progression
def on_button_click(event):
    global rotation_index
    vertices_indices = []
    
    # Step 1: Generate and place 5 TKR tiles
    if rotation_index < 5:
        vertices_indices = initialize_tkr_vertices(rotation_angle=angle_72 * rotation_index)
        draw_tile(vertices_indices, color='lightblue')
        update_tiled_angle(vertices_indices, tile_type='TKR')
        
    # Step 2: After 5 TKR tiles, start placing TNR tiles
    elif rotation_index >= 5:
        vertices_indices = place_tnr_tile()
        draw_tile(vertices_indices, color='lightgreen')
        update_tiled_angle(vertices_indices, tile_type='TNR')

    # Cleanly update the canvas and display the vertex table
    ax.set_title(f"Tile Progression: {rotation_index + 1}")
    fig.canvas.draw()

# Setup GUI
def setup_gui():
    button_ax = plt.axes([0.45, 0.01, 0.1, 0.05])
    button = Button(button_ax, 'Add Tile')
    button.on_clicked(on_button_click)
    plt.show()

# Start GUI and plotting
setup_gui()
