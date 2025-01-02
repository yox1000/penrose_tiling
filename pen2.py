import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.patches import Polygon
from matplotlib.widgets import Button

# Constants for angles
angle_72 = np.radians(72)
angle_108 = np.radians(108)
angle_144 = np.radians(144)
angle_36 = np.radians(36)

# Dictionary to store vertex positions with their indices
vertices_table = {}
current_vertex_index = 0
rotation_index = 0  # Track current rotation step

# Initialize Plot
fig, ax = plt.subplots()

# Rotate a point around an origin
def rotate_point(point, angle, origin=(0, 0)):
    ox, oy = origin
    px, py = point
    cos_theta, sin_theta = np.cos(angle), np.sin(angle)
    qx = ox + cos_theta * (px - ox) - sin_theta * (py - oy)
    qy = oy + sin_theta * (px - ox) + cos_theta * (py - oy)
    return np.array([qx, qy])

# Check if a vertex exists
def find_vertex(vertex, tolerance=1e-6):
    for index, existing_vertex in vertices_table.items():
        if np.allclose(vertex, existing_vertex, atol=tolerance):
            return index
    return None

# Initialize vertices with rotation for TKR tile
def initialize_tkr_vertices(position=(0, 0), rotation_angle=0):
    global current_vertex_index, vertices_table
    
    # Define the four vertices based on TKR geometry
    p0 = np.array(position)
    p1 = p0 + np.array([1, 0])
    p2 = p1 + np.array([np.cos(-angle_72), np.sin(-angle_72)])
    p3 = p2 + np.array([np.cos(-angle_72 - angle_108), np.sin(-angle_72 - angle_108)])
    
    vertices = [rotate_point(p, rotation_angle) for p in [p0, p1, p2, p3]]
    vertices_indices = []
    
    for vertex in vertices:
        vertex_index = find_vertex(vertex)
        if vertex_index is None:
            vertices_table[current_vertex_index] = vertex
            vertex_index = current_vertex_index
            ax.plot(vertex[0], vertex[1], 'o', color='blue')
            ax.text(vertex[0] + 0.05, vertex[1] + 0.05, 
                    f'{vertex_index}', ha='center', va='center', 
                    fontsize=9, color='blue')
            current_vertex_index += 1
        vertices_indices.append(vertex_index)
    
    ax.set_aspect('equal', 'box')
    return vertices_indices

# Draw TKR or TNR tile and fill it
def draw_tile(vertices_indices):
    polygon_vertices = [vertices_table[idx] for idx in vertices_indices]
    for i in range(len(vertices_indices)):
        start_vertex = vertices_table[vertices_indices[i]]
        end_vertex = vertices_table[vertices_indices[(i + 1) % len(vertices_indices)]]
        ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='black')
    polygon = Polygon(polygon_vertices, closed=True, color='lightblue', alpha=0.5)
    ax.add_patch(polygon)

# Position for TNR tile with correct angles and side length
def place_tnr_tile():
    global current_vertex_index, vertices_table
    
    # Fetch vertices 1, 2, and 10 to use in TNR
    p0 = vertices_table[1]  # Starting vertex 1
    p1 = vertices_table[2]  # Connect with vertex 2
    p2 = vertices_table[10]  # Known position for TNR orientation
    
    # Calculate fourth vertex by rotating p1 around p2 by 144 degrees to find new vertex p3 with side length 1
    p3 = rotate_point(p1, angle_144, origin=p2)  # New vertex at 144°

    # Log the vertices and calculated angles
    print(f"Vertex 1: {p0}, Vertex 2: {p1}, Vertex 10: {p2}, Calculated Vertex 11: {p3}")
    
    vertices = [p0, p1, p2, p3]
    vertices_indices = []
    for vertex in vertices:
        vertex_index = find_vertex(vertex)
        if vertex_index is None:
            vertices_table[current_vertex_index] = vertex
            vertex_index = current_vertex_index
            ax.plot(vertex[0], vertex[1], 'o', color='blue')
            ax.text(vertex[0] + 0.05, vertex[1] + 0.05, 
                    f'{vertex_index}', ha='center', va='center', 
                    fontsize=9, color='blue')
            current_vertex_index += 1
        vertices_indices.append(vertex_index)
    
    ax.set_aspect('equal', 'box')
    return vertices_indices

# Display vertices in a table with scrollbar
table_window = None
def display_vertices_table():
    global table_window
    if table_window and tk.Toplevel.winfo_exists(table_window):
        for widget in table_window.winfo_children():
            widget.destroy()
    else:
        table_window = tk.Toplevel()
        table_window.title("Vertices Table")

    columns = ('Index', 'X', 'Y')
    tree = ttk.Treeview(table_window, columns=columns, show='headings', height=15)
    tree.heading('Index', text='Index')
    tree.heading('X', text='X')
    tree.heading('Y', text='Y')

    # Add a scrollbar to the tree view
    scrollbar = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    for index, vertex in vertices_table.items():
        tree.insert('', tk.END, values=(index, round(vertex[0], 2), round(vertex[1], 2)))
    tree.pack(side="left", fill="both", expand=True)
    table_window.update_idletasks()

# Handle button click to add and rotate TKR tiles
def on_button_click(event):
    global rotation_index
    if rotation_index < 5:
        rotation_angle = rotation_index * -angle_72
        vertices_indices = initialize_tkr_vertices(rotation_angle=rotation_angle)
        draw_tile(vertices_indices)
    elif rotation_index == 5:
        tnr_indices = place_tnr_tile()  # Place TNR tile on 6th click
        draw_tile(tnr_indices)
    fig.canvas.draw()
    display_vertices_table()
    rotation_index += 1


# Adjusted function to generate the Thin Rhombus (TNR) tile and close with vertex 2
def generate_tnr_tile():
    global current_vertex_index

    # Step 1: Define the vertices 1, 2, and 10 for the TNR tile
    vertex_1 = vertices_table[1]
    vertex_2 = vertices_table[2]
    vertex_10 = vertices_table[10]

    # Step 2: Calculate the position of vertex 11 to complete the TNR tile
    side_length = 1
    angle_36 = np.radians(36)  # TNR tile characteristic angle

    # Calculate vector from vertex 10, rotated to achieve the 36-degree angle for the TNR side
    vector_10_to_1 = (vertex_1 - vertex_10) / np.linalg.norm(vertex_1 - vertex_10)
    rotation_matrix = np.array([[np.cos(angle_36), -np.sin(angle_36)], 
                                [np.sin(angle_36), np.cos(angle_36)]])
    vector_10_to_11 = np.dot(rotation_matrix, vector_10_to_1) * side_length
    vertex_11 = vertex_10 + vector_10_to_11

    # Step 3: Check if vertex 11 already exists, and if not, add it to the table
    vertex_11_index = find_vertex(vertex_11)
    if vertex_11_index is None:
        vertices_table[current_vertex_index] = vertex_11
        vertex_11_index = current_vertex_index
        current_vertex_index += 1
        # Plot vertex 11
        ax.plot(vertex_11[0], vertex_11[1], 'o', color='blue')
        ax.text(vertex_11[0] + 0.05, vertex_11[1] + 0.05,
                f'{vertex_11_index}', ha='center', va='center',
                fontsize=9, color='blue')

    # Step 4: Draw the TNR tile by specifying vertices 1, 2, 10, and 11 in correct order
    vertices_indices = [1, 2, 10, vertex_11_index]  # Ensure it starts at 1 and closes at 2
    draw_tile(vertices_indices)  # Use the general draw_tile function for TNR tile

# General draw_tile function to render any tile based on a list of vertex indices
def draw_tile(vertices_indices):
    polygon_vertices = [vertices_table[idx] for idx in vertices_indices]
    for i in range(len(vertices_indices)):
        start_vertex = vertices_table[vertices_indices[i]]
        end_vertex = vertices_table[vertices_indices[(i + 1) % len(vertices_indices)]]
        ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='black')
    polygon = Polygon(polygon_vertices, closed=True, color='lightgreen', alpha=0.5)
    ax.add_patch(polygon)

# Function to find if a vertex exists in the vertices table or not
def find_vertex(vertex):
    for index, existing_vertex in vertices_table.items():
        if np.allclose(vertex, existing_vertex, atol=1e-6):
            return index
    return None

ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Add Tile')
button.on_clicked(on_button_click)

plt.show()
