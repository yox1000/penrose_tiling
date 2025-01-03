import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

# Define the golden ratio
phi = (1 + np.sqrt(5)) / 2

# Define the vertices of the kite
fat_rhombus = np.array([
    [0, 0],                          # Vertex A (central point)
    [1, 0],                          # Vertex B
    [1 + np.cos(2*np.pi/5), np.sin(2*np.pi/5)],  # Vertex C
    [np.cos(2*np.pi/5), np.sin(2*np.pi/5)]  # Vertex D
])

thin_rhombus = np.array([
    [0,0],
    [1,0],
    [1+ np.cos(np.pi/5), np.sin(np.pi/5)],
    [np.cos(np.pi/5), np.sin(np.pi/5)]
])

#def subdivide_thin_rhombus(thin_rhombus):

#def subdivide_thick_rhombus(thick_rhombus):



def rotate_tile(tile, angle):
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)]
    ])
    return np.dot(tile, rotation_matrix)

# Global variables
current_iteration = 0
star = []

def create_star_shape():
    global current_iteration, star
    if current_iteration < 5:
        angle = 2 * np.pi * current_iteration / 5  # 72 degrees in radians
        rotated_kite = rotate_tile(fat_rhombus, angle)
        star.append(rotated_kite)
        current_iteration += 1
    return star

def update_plot(event):
    global star
    create_star_shape()  # Add the next kite
    ax.clear()  # Clear the current plot
    for tile in star:
        ax.fill(tile[:, 0], tile[:, 1], edgecolor='black', color = "g", alpha=0.6)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect('equal')
    plt.draw()

# Set up the plot
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.2)  # Adjust the plot area to make space for the button

# Add a button
ax_button = plt.axes([0.4, 0.05, 0.2, 0.075])  # Position of the button
button = Button(ax_button, 'Press for new tile')  # Create the button
button.on_clicked(update_plot)  # Link the button to the update_plot function

# Initial plot
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_aspect('equal')
plt.show()