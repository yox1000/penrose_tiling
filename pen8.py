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
tiles = []
rotation_state = 0
retired_vertices = set()

# Initialize Plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect('equal')

# Initialize Tkinter window for vertices table
table_window = tk.Toplevel()
table_window.title("Vertices Table")

# Columns for vertices table
columns = ('Index', 'X', 'Y', 'Status', 'Tiled Angle')
tree = ttk.Treeview(table_window, columns=columns, show='headings', height=15)
tree.heading('Index', text='Index')
tree.heading('X', text='X')
tree.heading('Y', text='Y')
tree.heading('Status', text='Status')
tree.heading('Tiled Angle', text='Tiled Angle')

# Adding scrollbar to the table
scrollbar = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tree.pack(side="left", fill="both", expand=True)

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
        if np.allclose(vertex, existing_vertex[:2], atol=tolerance):
            return index
    return None

def initialize_tile_vertices(position=(0, 0), rotation_angle=0, tile_type="TKR"):
    """Initializes vertices for TKR or TNR, rotates, plots, and labels them."""
    global current_vertex_index
    vertices = []
    if tile_type == "TKR":
        p0 = np.array(position)
        p1 = p0 + np.array([1, 0])
        p2 = p1 + np.array([np.cos(-angle_72), np.sin(-angle_72)])
        p3 = p2 + np.array([np.cos(-angle_72 - angle_108), np.sin(-angle_72 - angle_108)])
        vertices = [p0, p1, p2, p3]
    elif tile_type == "TNR":
        p0 = np.array(position)
        p1 = p0 + np.array([1, 0])
        p2 = rotate_point(p1, angle_144, origin=p0)
        p3 = rotate_point(p2, -angle_108, origin=p2)
        vertices = [p0, p1, p2, p3]

    rotated_vertices = [rotate_point(v, rotation_angle) for v in vertices]
    vertices_indices = []
    for vertex in rotated_vertices:
        vertex_index = find_vertex(vertex)
        if vertex_index is None:
            vertices_table[current_vertex_index] = (vertex[0], vertex[1], "Active", 0)
            vertex_index = current_vertex_index
            ax.plot(vertex[0], vertex[1], 'o', color='blue')
            ax.text(vertex[0] + 0.05, vertex[1] + 0.05, f'{vertex_index}', ha='center', va='center', fontsize=9, color='blue')
            current_vertex_index += 1
        vertices_indices.append(vertex_index)
    ax.set_aspect('equal', 'box')

    return vertices_indices

def draw_tile(vertices_indices, tile_type="TKR"):
    polygon_vertices = [vertices_table[idx][:2] for idx in vertices_indices]
    for i in range(len(vertices_indices)):
        start_vertex = vertices_table[vertices_indices[i]][:2]
        end_vertex = vertices_table[vertices_indices[(i + 1) % len(vertices_indices)]][:2]
        ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='black')
    
    color = 'lightblue' if tile_type == "TKR" else 'lightgreen'
    polygon = Polygon(polygon_vertices, closed=True, color=color, alpha=0.5)
    ax.add_patch(polygon)

    # Update tiled angles in table
    for idx in vertices_indices:
        angle_sum = vertices_table[idx][3] + (angle_72 if tile_type == "TKR" else angle_144)
        vertices_table[idx] = (*vertices_table[idx][:3], angle_sum)

# Refresh vertices table display
def display_vertices_table():
    for row in tree.get_children():
        tree.delete(row)
    for index, (x, y, status, angle) in vertices_table.items():
        tree.insert('', tk.END, values=(index, round(x, 2), round(y, 2), status, round(np.degrees(angle), 2)))

def on_button_click(event):
    global rotation_state, current_vertex_index
    if rotation_state < 5:  # First 5 TKR tiles
        rotation_angle = -rotation_state * 2 * angle_36  # Clockwise rotation
        position = (0, 0)  # Centered at origin
        vertices_indices = initialize_tile_vertices(position, rotation_angle, tile_type="TKR")
        draw_tile(vertices_indices)
        tiles.append({"vertices": vertices_indices, "type": "TKR"})

        if rotation_state == 4:  # Retire vertex 0 after 5th TKR
            vertices_table[0] = (*vertices_table[0][:3], "Retired")

    elif rotation_state < 10:  # Next 5 TNR tiles
        position = vertices_table[min(vertices_table)][0:2]
        rotation_angle = -rotation_state * angle_36
        vertices_indices = initialize_tile_vertices(position, rotation_angle, tile_type="TNR")
        draw_tile(vertices_indices, tile_type="TNR")
        tiles.append({"vertices": vertices_indices, "type": "TNR"})

    fig.canvas.draw()
    display_vertices_table()
    rotation_state += 1

# Button setup
ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Add Tile')
button.on_clicked(on_button_click)

# Show blank plot and table at start
display_vertices_table()
plt.show()
