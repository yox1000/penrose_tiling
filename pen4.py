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

# Dictionary to store vertex positions with their indices
vertices_table = {}
current_vertex_index = 0
rotation_index = 0  # Keep track of the current rotation step

# Initialize Plot
fig, ax = plt.subplots()

# Function to apply rotation matrix to a point
def rotate_point(point, angle, origin=(0, 0)):
    ox, oy = origin
    px, py = point
    cos_theta, sin_theta = np.cos(angle), np.sin(angle)
    qx = ox + cos_theta * (px - ox) - sin_theta * (py - oy)
    qy = oy + sin_theta * (px - ox) + cos_theta * (py - oy)
    return np.array([qx, qy])

# Function to check if a vertex already exists
def find_vertex(vertex, tolerance=1e-6):
    for index, existing_vertex in vertices_table.items():
        if np.allclose(vertex, existing_vertex, atol=tolerance):
            return index
    return None

# Initialize TKR vertices with rotation
def initialize_tkr_vertices(position=(0, 0), rotation_angle=0):
    global current_vertex_index, vertices_table
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

# Draw TKR tile and fill it
def draw_tkr_tile(vertices_indices):
    polygon_vertices = [vertices_table[idx] for idx in vertices_indices]
    for i in range(len(vertices_indices)):
        start_vertex = vertices_table[vertices_indices[i]]
        end_vertex = vertices_table[vertices_indices[(i + 1) % len(vertices_indices)]]
        ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='black')
    polygon = Polygon(polygon_vertices, closed=True, color='lightblue', alpha=0.5)
    ax.add_patch(polygon)

# Display vertices in a table window
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
    tree = ttk.Treeview(table_window, columns=columns, show='headings')
    tree.heading('Index', text='Index')
    tree.heading('X', text='X')
    tree.heading('Y', text='Y')

    for index, vertex in vertices_table.items():
        tree.insert('', tk.END, values=(index, round(vertex[0], 2), round(vertex[1], 2)))
    tree.pack()
    table_window.update_idletasks()

def on_button_click(event):
    global rotation_index
    rotation_angle = rotation_index * -angle_72
    vertices_indices = initialize_tkr_vertices(rotation_angle=rotation_angle)
    draw_tkr_tile(vertices_indices)
    fig.canvas.draw()
    display_vertices_table()
    rotation_index += 1

ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Add TKR Tile')
button.on_clicked(on_button_click)

plt.show()
