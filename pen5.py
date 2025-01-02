import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.patches import Polygon
from matplotlib.widgets import Button

# Constants
angle_72 = np.radians(72)
angle_108 = np.radians(108)
angle_144 = np.radians(144)
angle_36 = np.radians(36)

# Global dictionaries and variables
vertices_table = {}
current_vertex_index = 0
rotation_index = 0  # Track TKR tiles
vertex_connections = {}
retired_vertices = set()
table_window = None  # Initialize global table window

# Initialize Plot
fig, ax = plt.subplots()

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

# Initialize vertices for TKR tile
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
            vertices_table[current_vertex_index] = (vertex[0], vertex[1], "Active")
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

# Revised function to generate and plot the Thin Rhombus (TNR) tile
def place_tnr_tile():
    global current_vertex_index

    # Define vertices 1, 2, and 10 for the TNR tile
    vertex_1 = np.array(vertices_table[1][:2])
    vertex_2 = np.array(vertices_table[2][:2])
    vertex_10 = np.array(vertices_table[10][:2])

    # Calculate the position of vertex 11 for TNR
    vector_10_to_1 = (vertex_1 - vertex_10) / np.linalg.norm(vertex_1 - vertex_10)
    rotation_matrix = np.array([[np.cos(angle_36), -np.sin(angle_36)], 
                                [np.sin(angle_36), np.cos(angle_36)]])
    vertex_11 = vertex_10 + np.dot(rotation_matrix, vector_10_to_1)

    # Find or add vertex 11 to vertices_table
    vertex_11_index = find_vertex(vertex_11)
    if vertex_11_index is None:
        vertices_table[current_vertex_index] = (vertex_11[0], vertex_11[1], "Active")
        vertex_11_index = current_vertex_index
        current_vertex_index += 1
        ax.plot(vertex_11[0], vertex_11[1], 'o', color='blue')
        ax.text(vertex_11[0] + 0.05, vertex_11[1] + 0.05,
                f'{vertex_11_index}', ha='center', va='center',
                fontsize=9, color='blue')

    # Draw TNR tile with vertices [1, 2, 10, 11]
    vertices_indices = [1, 2, 10, vertex_11_index]
    draw_tile(vertices_indices, color='lightgreen')
    return vertices_indices

# Check and retire vertex if surrounded
def check_and_retire_vertex(vertex_index):
    if vertex_connections.get(vertex_index, 0) >= 5 and vertex_index not in retired_vertices:
        retired_vertices.add(vertex_index)
        vertices_table[vertex_index] = (*vertices_table[vertex_index][:2], "Retired")
        print(f"Vertex {vertex_index} is now retired.")

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

# Button click handler for tiles
def on_button_click(event):
    global rotation_index
    vertices_indices = []
    
    if rotation_index < 5:
        rotation_angle = rotation_index * -angle_72
        vertices_indices = initialize_tkr_vertices(rotation_angle=rotation_angle)
        draw_tile(vertices_indices, color='lightblue')
    elif rotation_index == 5:
        vertices_indices = place_tnr_tile()
        draw_tile(vertices_indices, color='lightgreen')
        check_and_retire_vertex(0)  # Retire vertex 0 after fifth tile
        check_and_retire_vertex(1)  # Retire vertex 1 if TNR completes it
    
    for vertex_index in vertices_indices:
        check_and_retire_vertex(vertex_index)

    fig.canvas.draw()
    display_vertices_table()
    rotation_index += 1

# Button setup
ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Add Tile')
button.on_clicked(on_button_click)

plt.show()
