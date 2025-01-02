import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
import pandas as pd

# Constants for angles
angle_72 = np.radians(72)
angle_108 = np.radians(108)

# Table to store vertex positions for each tile
vertices_table = {}  # Maps vertex index to coordinates
current_vertex_index = 0  # Starting index for vertices

# 1. Tile Class Definition with Consistent Vertex Labeling
class PenroseTile:
    def __init__(self, vertices, tile_type, position=(0, 0)):
        global current_vertex_index, vertices_table
        self.vertices = []
        self.tile_type = tile_type
        self.position = position

        # Register each vertex with unique indices if not already present
        for vertex in vertices:
            # Check if vertex position exists in vertices_table
            found_index = None
            for idx, pos in vertices_table.items():
                if np.allclose(pos, vertex + np.array(position)):
                    found_index = idx
                    break
            
            # Use existing index if vertex position exists
            if found_index is not None:
                self.vertices.append(found_index)
            else:
                vertices_table[current_vertex_index] = vertex + np.array(position)
                self.vertices.append(current_vertex_index)
                current_vertex_index += 1

# Function to Create TKR Tile with 4 Sides in 4th Quadrant
def create_tkr(position=(0, 0)):
    # Map vertices starting along the positive x-axis, rotating clockwise
    # Starting point at origin
    p0 = np.array(position)  # Origin
    
    # Define angles in radians
    angle_72 = np.radians(72)
    angle_108 = np.radians(108)

    # First side along the positive x-axis (1 unit)
    p1 = p0 + np.array([1, 0])  # Move 1 unit along x-axis

    # Calculate p2: rotate -72° (clockwise) from p1, length 1
    p2 = p1 + np.array([
        np.cos(-angle_72),
        np.sin(-angle_72)
    ])

    # Calculate p3: rotate -108° (clockwise) from p2, length 1
    p3 = p2 + np.array([
        np.cos(-angle_72 - angle_108),
        np.sin(-angle_72 - angle_108)
    ])

    # Combine vertices to form the TKR
    vertices = np.array([p0, p1, p2, p3, p0])  # Close the shape

    return vertices  # Returns vertices for the TKR

# Visualization Setup
def setup_visualization():
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.subplots_adjust(bottom=0.2)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.plot(0, 0, 'ro')  # Origin point
    return fig, ax

# Visualization Function
def visualize(tiles, ax):
    ax.cla()  # Clear axes
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.plot(0, 0, 'ro')  # Origin point

    for tile in tiles:
        coords = np.array([vertices_table[idx] for idx in tile.vertices])
        ax.fill(coords[:, 0], coords[:, 1], color='green' if tile.tile_type == 'TKR' else 'blue',
                alpha=0.5, edgecolor='black')

    ax.set_aspect('equal')
    ax.grid(True)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.draw()  # Update plot

# Button Callback for Adding TKR Tile
def on_button_click(event):
    global tiles
    new_vertices = create_tkr(position=(0, 0))  # Starting from origin in the 4th quadrant
    new_tile = PenroseTile(vertices=new_vertices, tile_type='TKR', position=(0, 0))
    tiles.append(new_tile)

    # Update visualization and display vertex table
    visualize(tiles, ax)
    display_vertex_table()  # Display or update vertex table in separate window

# Display Vertex Table in Separate Window
def display_vertex_table():
    vertex_data = pd.DataFrame(vertices_table.items(), columns=['Index', 'Coordinates'])
    vertex_data['Coordinates'] = vertex_data['Coordinates'].apply(lambda x: tuple(np.round(x, 2)))  # Format coordinates

    fig, ax_table = plt.subplots()
    ax_table.axis('off')
    table = ax_table.table(cellText=vertex_data.values, colLabels=vertex_data.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    fig.canvas.manager.set_window_title("Vertex Table")  # Set a specific window title for clarity
    plt.show()  # Show the vertex table window
    fig.show()  # Make sure the figure is shown

# Main Execution
if __name__ == "__main__":
    tiles = []
    fig, ax = setup_visualization()

    ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
    button = Button(ax_button, 'Add Tile')
    button.on_clicked(on_button_click)

    plt.ion()  # Turn interactive mode on 
    visualize(tiles, ax)
    plt.title("Penrose Tiling: Add Tiles in 4th Quadrant")
    plt.show()
    input("Press Enter to exit...") # Keep the window open
