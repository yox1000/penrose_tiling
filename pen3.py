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

#################################################################
# Helper Functions (rotate_point, find_vertex)
#################################################################

def rotate_point(point, angle, origin=(0, 0)):
    """Rotates a point counterclockwise by a given angle around a given origin."""
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

#################################################################
# Tile Initialization, Drawing, and Vertex Management
#################################################################

def initialize_tile_vertices(position=(0, 0), rotation_angle=0, tile_type="TKR"):
    """Initializes vertices for TKR or TNR, rotating, plotting, and updating tiled angles."""
    global current_vertex_index
    vertices = []
    
    # Define tile vertices based on type
    if tile_type == "TKR":
        # Define TKR vertices in sequence
        p0 = np.array(position)
        p1 = p0 + np.array([1, 0])
        p2 = p1 + np.array([np.cos(-angle_72), np.sin(-angle_72)])
        p3 = p2 + np.array([np.cos(-angle_72 - angle_108), np.sin(-angle_72 - angle_108)])
        vertices = [p0, p1, p2, p3]
    
    elif tile_type == "TNR":
        p0 = np.array(position)
        last_placed_vertex = list(vertices_table.keys())[-1] #Access last placed vertex
        next_vertex_index = find_next_vertex(last_placed_vertex) #Call find_next_vertex with correct parameter
        if next_vertex_index is None: #If no next available vertex is found implement level up logic
            min_index = min([v for v in vertices_table if vertices_table[v][2] == "Active"])
            if min_index is not None:  # Find next vertex starting at the minimum index

                next_vertex = find_next_vertex(min_index)
                if next_vertex is not None: #If next available vertex was found proceed with TNR placement
                    p1 = vertices_table[next_vertex][:2] # Get p1 coordinates
                    vertices = place_tnr_at_level(vertices_table[min_index][:2], p1) #Generate TNR tile vertices


                else:  # Start a new level with a TKR tile


                  return initialize_tile_vertices(position=vertices_table[min_index][:2], rotation_angle=0, tile_type="TKR")  # Place TKR at new level

        else:  # No Level up, place the TNR tile
            p1 = vertices_table[next_vertex_index][:2]
            v0_to_p1 = p1 - p0
            p3 = rotate_point(p1, angle_144, origin=p0)

            next_next_vertex_index = find_next_vertex(next_vertex_index)  # Find next vertex for p2 from p1

            if next_next_vertex_index is not None:
                p2 = vertices_table[next_next_vertex_index][:2]
            else: # No available vertex on current level, find next lowest active vertex on the next level


                min_index = min([v for v in vertices_table if vertices_table[v][2] == "Active"])
                p2 = vertices_table[min_index][:2] # Get coordinates of the lowest available active vertex

            vertices = [p0, p1, p2, p3]  # Define vertices for the TNR tile.
    
    # Rotate vertices based on angle and add to plot
    rotated_vertices = [rotate_point(v, rotation_angle) for v in vertices]
    
    vertices_indices = []
    for vertex in rotated_vertices:
        vertex_index = find_vertex(vertex)
        
        # Add new vertex if it does not exist
        if vertex_index is None:
            vertices_table[current_vertex_index] = (vertex[0], vertex[1], "Active", 0, set())
            vertex_index = current_vertex_index
            ax.plot(vertex[0], vertex[1], 'o', color='blue')
            ax.text(vertex[0] + 0.05, vertex[1] + 0.05, f'{vertex_index}', ha='center', va='center', fontsize=9, color='blue')
            current_vertex_index += 1
        
        vertices_indices.append(vertex_index)
    
    # Update tiled angles and connections
    update_tiled_angles(vertices_indices, tile_type)
    update_vertex_connections(vertices_indices)
    
    return vertices_indices

def draw_tile(vertices_indices, tile_type="TKR"):
    """Draws a tile on the plot based on its vertices and type."""
    polygon_vertices = [vertices_table[idx][:2] for idx in vertices_indices]  # Extract x, y coordinates
    # Draw edges
    for i in range(len(vertices_indices)):
        start_vertex = vertices_table[vertices_indices[i]][:2] # Extract the start vertex coordinates
        end_vertex = vertices_table[vertices_indices[(i + 1) % len(vertices_indices)]][:2] # Calculate end vertex with wrap-around.
        ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='black')
    # Set tile color based on type
    color = 'lightblue' if tile_type == "TKR" else 'lightgreen'
    # Create and add polygon
    polygon = Polygon(polygon_vertices, closed=True, color=color, alpha=0.5)
    ax.add_patch(polygon)
    ax.set_aspect('equal', 'box')  # Ensure equal aspect ratio for visualization

# Display vertices in a table with scrollbar, 'Tiled Angle', and 'Connections' columns
table_window = None  # Make absolutely sure this is at the top level

# Display vertices in a table with scrollbar, 'Tiled Angle', and 'Connections' columns
def display_vertices_table():
    """Displays the vertices and their coordinates in a separate, resizable Tkinter window."""
    global table_window
    if table_window and tk.Toplevel.winfo_exists(table_window):
        for widget in table_window.winfo_children():
            widget.destroy()
    else:
        table_window = tk.Toplevel()
        table_window.title("Vertices Table")
        table_window.geometry("500x400") # Set initial size (adjust as needed)
    columns = ('Index', 'X', 'Y', 'Status', 'Tiled Angle', 'Connections')
    tree = ttk.Treeview(table_window, columns=columns, show='headings', height=15)
    tree.heading('Index', text='Index')
    tree.heading('X', text='X')
    tree.heading('Y', text='Y')
    tree.heading('Status', text='Status')
    tree.heading('Tiled Angle', text='Tiled Angle')
    tree.heading('Connections', text='Connections')
    for index, (x, y, status, tiled_angle, connections) in vertices_table.items():
        tree.insert('', tk.END, values=(index, round(x, 2), round(y, 2), status, round(math.degrees(tiled_angle) % 360, 2), connections))
    scrollbar = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)  # Allow resizing
    table_window.update_idletasks()

#Placement of this function within the code:
# The `display_vertices_table` function should be defined at the top level of your script, along with the other function definitions. 
# Specifically, it should be defined *after* any helper functions it uses (like `find_vertex`) but *before* the main execution block of your code.
# This placement ensures that all functions are defined before being called, 
# which should help prevent the "not defined" errors that occur due to Python's sequential execution.

#################################################################
# Next Vertex Finding Logic and TNR Angle Calculation
#################################################################

def find_next_vertex(start_vertex):
    """Finds the next clockwise active vertex connected to the given start_vertex."""
    potential_vertices = []  #Store potential next vertices
    v0 = vertices_table[start_vertex][:2] # Get coordinates of the start_vertex
    for vertex_index, vertex_coords in vertices_table.items():
        if vertex_index != start_vertex and vertex_coords[2] == "Active":  #Consider only active vertices other than the start vertex
            v_next = vertex_coords[:2]  # Extract coordinates
            angle = math.atan2(np.cross(np.array([1, 0]), v_next - v0), np.dot(np.array([1, 0]), v_next - v0))
            if angle < 0:  # Clockwise angle (negative in this cross-product setup)
                potential_vertices.append((vertex_index, angle))  #Store potential vertices and their angles relative to v0
    # Sort potential vertices by angle to find the smallest clockwise one.
    potential_vertices.sort(key=lambda x: x[1], reverse=True)  #Sort in descending order (clockwise)
    if potential_vertices:
        return potential_vertices[0][0]  # Return the index of the next clockwise vertex
    else:
        return None  # Return None if no suitable next potential vertices are found

def calculate_tnr_rotation_angle(start_vertex, next_vertex):
    """Calculates the correct rotation angle for TNR placement."""
    v_start = np.array(vertices_table[start_vertex][:2]) # Extract starting vertex coordinates
    v_next = np.array(vertices_table[next_vertex][:2])  # Extract next vertex coordinates
    tnr_side = v_next - v_start  # Vector representing the first side of the TNR
    angle = math.atan2(tnr_side[1], tnr_side[0]) # Angle of the vector representing the first side of TNR
    return angle - angle_36  # Subtract 36 degrees (the acute angle of the TNR) to correctly orient the TNR
    
def update_tiled_angles(vertices_indices, tile_type):
    """Updates tiled angles, handling TKR and TNR correctly."""
    global vertices_table #Add this line
    if tile_type == "TKR":
        for vertex_index in vertices_indices:
            if vertices_table[vertex_index][2] == "Active":
                x, y, status, current_angle, connections = vertices_table[vertex_index]  #Correct values unpacking
                if vertex_index == 0 and rotation_state < 5: #Check if vertex_index is the starting vertex (vertex 0) for the first 5 tiles (TKR tiles around the origin)
                    increment = angle_72
                elif vertex_index in vertices_indices[1:4:2]:  # New vertices of TKR tile
                    increment = angle_108
                else:
                    increment = angle_72 # For existing vertices of TKR tiles
                vertices_table[vertex_index] = (x, y, status, current_angle + increment, connections) #Correctly update angle


    elif tile_type == "TNR":
        for vertex_index in vertices_indices:

            if vertices_table[vertex_index][2] == "Active":

                x, y, status, current_angle, connections = vertices_table[vertex_index]  #Correct values unpacking
                if vertex_index == vertices_indices[0] or vertex_index == vertices_indices[2]:  # Use correct vertices
                    increment = angle_36  # Update by adding 36 degrees to the current_angle

                else:

                    increment = angle_144  # Vertices p1 and p3 in TNR

                vertices_table[vertex_index] = (x, y, status, current_angle + increment, connections) #Correctly update tiled angle and add the set for connections

def update_vertex_connections(vertices_indices):
    """Updates vertex connections and retires vertices when necessary."""
    global vertex_connections
    for i in range(len(vertices_indices)):
        v1 = vertices_indices[i]
        v2 = vertices_indices[(i + 1) % len(vertices_indices)]  # Use modulo for wrap-around connection        
        # Update connections for both vertices
        if v2 not in vertices_table[v1][4]: # Check if connection already exists before adding.
            vertices_table[v1][4].add(v2)
            vertex_connections[v1] = vertex_connections.get(v1, 0) + 1
        if v1 not in vertices_table[v2][4]: # Check if connection already exists before adding.
            vertices_table[v2][4].add(v1)
            vertex_connections[v2] = vertex_connections.get(v2, 0) + 1  #Add connection even if the same as previous one
        # Retire vertex if it has 5 connections and it is not the central vertex
        if vertex_connections[v1] >= 5 and v1 != 0 and vertices_table[v1][2] == 'Active':  #Check if v1 needs to be retired
                x, y, _, angle, connections = vertices_table[v1]
                vertices_table[v1] = (x, y, "Retired", angle, connections)
                print(f"Vertex {v1} retired.")  # Print statement is not indented.
        if vertex_connections[v2] >= 5 and v2 != 0 and vertices_table[v2][2] == 'Active': #Check if v2 needs to be retired
                x, y, _, angle, connections = vertices_table[v2]
                vertices_table[v2] = (x, y, "Retired", angle, connections)
                print(f"Vertex {v2} retired.") # Print statement is not indented.

def find_next_available_vertex():
    """Finds the next lowest indexed active vertex or the next lowest available active vertex for the new level."""

    #Sort the dictionary of vertices_table keys in ascending order and get only the indices (keys).
    sorted_indices = sorted(vertices_table.keys())  

    for index in sorted_indices:
        if vertices_table[index][2] == "Active": #Search for available active vertices in ascending order of index.


            if find_next_vertex(index) is not None:  # Check if there's a clockwise connected and active vertex to the current index.

                return index #Return the lowest active index if a next one was found from it.



    return None  # Return None if no suitable next vertex is found (all vertices might be retired).

def place_tnr_at_level(p0, p1):

  """Place a TNR tile at the new level."""


  v0_to_p1 = p1 - p0 # Calculate the vector from p0 to p1

  p3 = rotate_point(p1, angle_144, origin=p0)  # Rotate p1 around p0 by 144 degrees to get p3



  next_next_vertex_index = find_next_vertex(find_vertex(p1))  # Find next vertex clockwise from p1
  if next_next_vertex_index is not None:

      p2 = vertices_table[next_next_vertex_index][:2] # Set p2 correctly

  else:

      min_index = min([v for v in vertices_table if vertices_table[v][2] == "Active"]) # Find lowest index
      p2 = vertices_table[min_index][:2] # Set p2 correctly



  return [p0, p1, p2, p3]  # Return vertices in correct order for TNR placement

#################################################################
# Button Click Handler and Main Tiling Logic
#################################################################
def on_button_click(event):

    """Handles button clicks to generate and draw tiles based on rotation state."""

    global rotation_state, current_vertex_index, rotation_index  # Declare global variables modified in this function

    if rotation_state < 5:
        rotation_angle = -rotation_state * 2 * angle_36  # Clockwise rotation
        position = (0, 0)  # Centered at origin
        vertices_indices = initialize_tile_vertices(position, rotation_angle, tile_type="TKR")  # Initialize TKR tile vertices
        draw_tile(vertices_indices, tile_type="TKR")  # Draw TKR tile with correct parameters

        tiles.append({"vertices": vertices_indices, "type": "TKR"})  # Append tile information

        if rotation_state == 4:  # Retire vertex 0 after 5th TKR tile is added

            vertices_table[0] = (*vertices_table[0][:3], vertices_table[0][3], vertices_table[0][4]) #Retire the vertex
            display_vertices_table() #Update the table

    elif rotation_state < 10:  # Correct TNR placement logic

        if tiles:
          start_vertex = tiles[-1]["vertices"][1]
        else:  # Handle case where tiles list might be empty on the first button click
          start_vertex = min([vertex for vertex, (_, _, status, _, _) in vertices_table.items() if status == "Active"])
        
        next_vertex = find_next_vertex(start_vertex) #Start from latest tile plotted

        if next_vertex is not None:  # Corrected placement logic


            rotation_angle = calculate_tnr_rotation_angle(start_vertex, next_vertex)
            tnr_vertices = initialize_tile_vertices(position=vertices_table[start_vertex][:2], rotation_angle=rotation_angle, tile_type="TNR")
            if tnr_vertices:

                draw_tile(tnr_vertices, tile_type="TNR")

                tiles.append({"vertices": tnr_vertices, "type": "TNR"})
    elif rotation_state >= 10: #Next levels generation
        start_vertex_index = find_next_available_vertex()

        if start_vertex_index is not None:  # If next level start vertex found.

            next_vertex = find_next_vertex(start_vertex_index)


            if next_vertex is not None: # If a next vertex is found

                rotation_angle = calculate_tnr_rotation_angle(start_vertex_index, next_vertex) # Angle from start to next
                if rotation_state % 5 == 0:  # Every fifth tile is a TKR
                    tile_type = "TKR"  # Set correct tile_type

                else:

                    tile_type = "TNR" # Set correct tile_type


                vertices_indices = initialize_tile_vertices(position=vertices_table[start_vertex_index][:2], rotation_angle=rotation_angle, tile_type=tile_type) #Call function here
                draw_tile(vertices_indices, tile_type=tile_type)
                tiles.append({"vertices": vertices_indices, "type": tile_type}) # Append tile information

    fig.canvas.draw()
    if rotation_state != 4: # Avoid double call

        display_vertices_table() # Correct placement
    rotation_index += 1  # Increment rotation_index

    rotation_state += 1   # Increment rotation_state

#################################################################
# Vertices Table Display
#################################################################

def display_vertices_table():
    """Displays the vertices table in a separate Tkinter window."""
    global table_window
    if table_window and tk.Toplevel.winfo_exists(table_window):
        for widget in table_window.winfo_children():
            widget.destroy()  # Clear existing table data
    else:
        table_window = tk.Toplevel()  # Remove figsize
        table_window.title("Vertices Table")
        table_window.geometry("400x300")  # Set window size using geometry (adjust as needed)
    # Define columns
    columns = ('Index', 'X', 'Y', 'Status', 'Tiled Angle', 'Connections')
    tree = ttk.Treeview(table_window, columns=columns, show='headings', height=15)  #Specify columns to display
    # Set column headings
    tree.heading('Index', text='Index')
    tree.heading('X', text='X')
    tree.heading('Y', text='Y')
    tree.heading('Status', text='Status')
    tree.heading('Tiled Angle', text='Tiled Angle')
    tree.heading('Connections', text='Connections')  # New 'Connections' column
    # Insert vertex data
    for index, (x, y, status, tiled_angle, connections) in vertices_table.items():
        tree.insert('', tk.END, values=(index, round(x, 2), round(y, 2), status, round(math.degrees(tiled_angle) % 360, 2), connections))
    # Add a scrollbar
    scrollbar = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)  # Link scrollbar to the Treeview widget.
    scrollbar.pack(side="right", fill="y") # Correctly pack the scrollbar to the right to align with the table.
    tree.pack(side="left", fill="both", expand=True)  # Pack the treeview widget
    table_window.update_idletasks()  # Update table display

#################################################################
# Plot Initialization, Button Setup, and Main Event Loop
#################################################################

# Initialize Plot (No initial tile plotted here)
fig, ax = plt.subplots(figsize=(8, 8))  # Correct placement
ax.set_aspect('equal')  # Ensure equal aspect ratio

# Button setup
ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Add Tile')
button.on_clicked(on_button_click)

display_vertices_table()
plt.show()

# Initialize and plot the first TKR tile
initial_vertices = initialize_tile_vertices(tile_type="TKR")  # Initialize with tile_type
draw_tile(initial_vertices, tile_type="TKR")  # Add tile_type parameter
tiles.append({"vertices": initial_vertices, "type": "TKR"})  # Append tile information. Call after draw_tile