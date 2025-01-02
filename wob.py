import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
import pandas as pd

angle_72 = np.radians(72)
angle_108 = np.radians(108)

vertices_table = {}
current_vertex_index = 0
edges = {}
tiles = []
vertex_table_fig = None

### Tile Class with Debugging ###
class PenroseTile:
    def __init__(self, vertices, tile_type, position=(0, 0)):
        global current_vertex_index, vertices_table, edges
        self.vertices = []
        self.tile_type = tile_type
        self.position = position

        # Register vertices in clockwise order
        for vertex in vertices:
            found_index = None
            for idx, pos in vertices_table.items():
                if np.allclose(pos, vertex + np.array(position)):
                    found_index = idx
                    break
            
            if found_index is not None:
                self.vertices.append(found_index)
            else:
                vertices_table[current_vertex_index] = vertex + np.array(position)
                self.vertices.append(current_vertex_index)
                current_vertex_index += 1

        # Debugging output for vertices
        print(f"Tile created with vertices: {[vertices_table[v] for v in self.vertices]}")
        
        self.register_edges()

    def register_edges(self):
        global edges
        num_vertices = len(self.vertices)
        for i in range(num_vertices - 1):
            edge = (self.vertices[i], self.vertices[i + 1])
            reverse_edge = (self.vertices[i + 1], self.vertices[i])

            if edge not in edges and reverse_edge not in edges:
                edges[edge] = True
                edges[reverse_edge] = True

### Tile Creation Functions ###
def create_tkr(position=(0, 0)):
    p0 = np.array(position)
    p1 = p0 + np.array([1, 0])
    p2 = p1 + np.array([np.cos(-angle_72), np.sin(-angle_72)])
    p3 = p2 + np.array([np.cos(-angle_72 - angle_108), np.sin(-angle_72 - angle_108)])
    vertices = np.array([p0, p1, p2, p3, p0])
    print(f"TKR vertices at position {position}: {vertices}")
    return vertices

def create_tnr(position=(0, 0)):
    p0 = np.array(position)
    p1 = p0 + np.array([1, 0])
    p2 = p1 + np.array([np.cos(angle_108), np.sin(angle_108)])
    p3 = p2 + np.array([np.cos(2 * angle_108), np.sin(2 * angle_108)])
    vertices = np.array([p0, p1, p2, p3, p0])
    print(f"TNR vertices at position {position}: {vertices}")
    return vertices

### Tile Addition Mechanism ###
def on_button_click(event):
    global tiles, edges
    new_tile_type = "TKR" if len(tiles) % 2 == 0 else "TNR"
    added_tile = False

    for tile in tiles:
        available_edge = find_clockwise_available_edge(tile)
        if available_edge:
            new_position = vertices_table[available_edge[1]]
            new_vertices = create_tkr(new_position) if new_tile_type == "TKR" else create_tnr(new_position)
            new_tile = PenroseTile(vertices=new_vertices, tile_type=new_tile_type, position=new_position)
            tiles.append(new_tile)
            added_tile = True
            break

    if not added_tile:
        outward_vertex = find_most_outward_vertex()
        if outward_vertex is not None:
            new_vertices = create_tkr(outward_vertex) if new_tile_type == "TKR" else create_tnr(outward_vertex)
            new_tile = PenroseTile(vertices=new_vertices, tile_type=new_tile_type, position=outward_vertex)
            tiles.append(new_tile)

    visualize(tiles, ax)
    display_vertex_table()

def find_clockwise_available_edge(tile):
    global edges
    for i in range(len(tile.vertices) - 1):
        edge = (tile.vertices[i], tile.vertices[i + 1])
        reverse_edge = (tile.vertices[i + 1], tile.vertices[i])
        if edges.get(edge) is False:
            return edge
    return None

def find_most_outward_vertex():
    max_distance = 0
    outward_vertex = None
    for idx, coords in vertices_table.items():
        dist = np.linalg.norm(coords)
        if dist > max_distance:
            max_distance = dist
            outward_vertex = coords
    return outward_vertex

### Visualization and Table Display with Debugging ###
def visualize(tiles, ax):
    ax.clear()
    for tile in tiles:
        vertices = [vertices_table[v] for v in tile.vertices]
        polygon = plt.Polygon(vertices, closed=True, edgecolor='black', facecolor='lightblue' if tile.tile_type == "TKR" else 'lightgreen')
        ax.add_patch(polygon)
    plt.draw()

def display_vertex_table():
    global vertex_table_fig

    if not vertices_table:
        print("No vertices to display in the table.")
        return

    if vertex_table_fig is None:
        vertex_table_fig, ax_table = plt.subplots(figsize=(6, 4))
        vertex_table_fig.canvas.manager.set_window_title("Vertex Table")
    else:
        ax_table = vertex_table_fig.gca()
        ax_table.clear()

    ax_table.axis('off')
    vertex_data = pd.DataFrame(vertices_table.items(), columns=['Index', 'Coordinates'])
    vertex_data['Coordinates'] = vertex_data['Coordinates'].apply(lambda x: tuple(np.round(x, 2)))

    table = ax_table.table(cellText=vertex_data.values, colLabels=vertex_data.columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)
    vertex_table_fig.canvas.draw()
    vertex_table_fig.show()

### Initialization and Start Plot Window ###
fig, ax = plt.subplots()
ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Add Tile')
button.on_clicked(on_button_click)

plt.show()

# Initial TKR tile creation and visualization
initial_vertices = create_tkr()
initial_tile = PenroseTile(vertices=initial_vertices, tile_type="TKR")
tiles.append(initial_tile)

visualize(tiles, ax)
display_vertex_table()

while plt.fignum_exists(fig.number):
    plt.pause(0.1)
