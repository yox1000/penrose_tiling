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
retired_vertices = set()

# Initialize Plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect('equal')  # Ensure equal aspect ratio

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
        next_vertex_index = find_next_vertex(list(vertices_table.keys())[-1])
        if next_vertex_index is None: # If there is no vertex left on the current level
          min_index = min(vertices_table.keys()) # Find vertex with min index on current level
          next_vertex_index = find_next_vertex(min_index) 
          p0 = vertices_table[min_index][:2] #Use min vertex as origin for next level


        p1 = vertices_table[next_vertex_index][:2]

        v0_to_p1 = p1 - p0
        p3 = rotate_point(p1, angle_144, origin=p0) # Rotate by 144 degrees for TNR


        next_next_vertex_index = find_next_vertex(next_vertex_index) #Find vertex with smallest clockwise angle from previous vertex
        if next_next_vertex_index is not None:
          p2 = vertices_table[next_next_vertex_index][:2]
          vertices = [p0, p1, p2, p3]


    rotated_vertices = [rotate_point(v, rotation_angle) for v in vertices]
    vertices_indices = []
    for vertex in rotated_vertices:
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

def draw_tile(vertices_indices, tile_type="TKR"):
    polygon_vertices = [vertices_table[idx][:2] for idx in vertices_indices]
    for i in range(len(vertices_indices)):
        start_vertex = vertices_table[vertices_indices[i]][:2]
        end_vertex = vertices_table[vertices_indices[(i + 1) % len(vertices_indices)]][:2]
        ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='black')
    
    color = 'lightblue' if tile_type == "TKR" else 'lightgreen'
    polygon = Polygon(polygon_vertices, closed=True, color=color, alpha=0.5)
    ax.add_patch(polygon)

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

def find_next_vertex(start_vertex):
    """Finds the next clockwise vertex."""

    potential_vertices = []
    v0 = vertices_table[start_vertex][:2] #Extract starting vertex coordinates
    for vertex_index, vertex_coords in vertices_table.items():
        if vertex_index != start_vertex and vertex_coords[2] == "Active": # Exclude start_vertex and non active
            v_next = vertex_coords[:2]
            angle = math.atan2(np.cross(np.array([1, 0]), v_next - v0), np.dot(np.array([1, 0]), v_next - v0))

            if angle < 0:  # Clockwise angle is negative
                potential_vertices.append((vertex_index, angle))
    # Sort by angle to find the closest clockwise vertex
    potential_vertices.sort(key=lambda x: x[1], reverse=True)  # Sort clockwise

    if potential_vertices:
        return potential_vertices[0][0]  # Return vertex index
    else:
        return None  # Handle case when no next vertex is found

def calculate_tnr_rotation_angle(start_vertex, next_vertex):
    """Calculates correct rotation angle for TNR placement."""
    v_start = vertices_table[start_vertex][:2]  #Starting vertex coords
    v_next = vertices_table[next_vertex][:2] #Next vertex coords
    tnr_side = v_next - v_start #Side of TNR
    angle = math.atan2(tnr_side[1], tnr_side[0]) #Angle of the TNR side
    return angle - angle_36  #Subtract 36 to correctly orient TNR

def on_button_click(event):
    global rotation_state, current_vertex_index
    if rotation_state < 5:  # First 5 TKR tiles

        rotation_angle = -rotation_state * 2 * angle_36  # Clockwise rotation
        position = (0, 0)  # Centered at origin
        vertices_indices = initialize_tile_vertices(position, rotation_angle, tile_type="TKR")
        draw_tile(vertices_indices)
        tiles.append({"vertices": vertices_indices, "type": "TKR"})

        if rotation_state == 4:  # Retire vertex 0 after 5th TKR
            vertices_table[0] = (*vertices_table[0][:2], "Retired")
            display_vertices_table()  # Update table immediately

    elif rotation_state < 10:  # Next 5 TNR tiles
        start_vertex = (rotation_state - 4) #Start from vertex 1
        next_vertex = find_next_vertex(start_vertex) #Find next vertex for TNR
        if next_vertex is not None:
            rotation_angle = calculate_tnr_rotation_angle(start_vertex, next_vertex)
            tnr_vertices = initialize_tile_vertices(position=vertices_table[start_vertex][:2], rotation_angle=rotation_angle, tile_type="TNR")
            draw_tile(tnr_vertices, tile_type="TNR") #Correct parameters
            tiles.append({"vertices": tnr_vertices, "type": "TNR"})
    elif rotation_state == 10:
        print("Decagon complete!")
        #Now code needs to identify the lowest available and connected vertex and plot a new TKR tile at 72 from previous one...
    elif rotation_state > 10 and rotation_state < 15:
      available_vertices = [v for v in vertices_table if vertices_table[v][2] == "Active"]
      if available_vertices:
        start_vertex = min(available_vertices, key=lambda x: x if x is not None else float('inf'))
        next_vertex = find_next_vertex(start_vertex)  # Find next connected vertex
        if next_vertex is not None:  # Make sure next_vertex is available

            rotation_angle = calculate_tnr_rotation_angle(start_vertex, next_vertex) # Angle from start to next
            tnr_vertices = initialize_tile_vertices(position=vertices_table[start_vertex][:2], rotation_angle=rotation_angle, tile_type="TNR")
            draw_tile(tnr_vertices, tile_type="TNR")  # Correct tile type and vertices
            tiles.append({"vertices": tnr_vertices, "type": "TNR"})
    else:
        print("Further tiling logic needed.")

    fig.canvas.draw()
    if rotation_state != 4: #Avoid redundant call
        display_vertices_table() #Refresh after change

    rotation_state += 1

# Button setup
ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Add Tile')
button.on_clicked(on_button_click)

# Initial TKR Tile
initial_vertices = initialize_tile_vertices()
draw_tile(initial_vertices)
tiles.append({"vertices": initial_vertices, "type": "TKR"})

plt.show()