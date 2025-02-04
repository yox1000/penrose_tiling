import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from collections import deque

#golden ratio
phi = (1 + np.sqrt(5)) / 2
angle_72 = np.deg2rad(72)
angle_108 = np.deg2rad(108)
angle_36 = np.radians(36)
angle_144 = np.radians(144)

# Define the vertices of the fat rhombus
fat_rhombus = np.array([
    [0, 0],                          # Vertex A (central point)
    [1, 0],                          # Vertex B
    [1 + np.cos(2*np.pi/5), np.sin(2*np.pi/5)],  # Vertex D
    [np.cos(2*np.pi/5), np.sin(2*np.pi/5)],  # Vertex C
    [0, 0]  # Close the shape
])

thin_rhombus = np.array([
    [0, 0],                          # Vertex A (central point)
    [1, 0],                          # Vertex B
    [1 + np.cos(np.pi/5), np.sin(np.pi/5)],  # Vertex D
    [np.cos(np.pi/5), np.sin(np.pi/5)],  # Vertex C
    [0, 0]


])

# Function to reflect a point over a line
def reflect_point_over_line(point, line_start, line_end):
    point = np.array(point)
    line_start = np.array(line_start)
    line_end = np.array(line_end)
    
    # Direction vector of the line
    line_dir = line_end - line_start
    line_length = np.linalg.norm(line_dir)
    line_dir_normalized = line_dir / line_length
    
    # Vector from line_start to the point
    point_vector = point - line_start
    
    # Project the point onto the line
    projection = np.dot(point_vector, line_dir_normalized) * line_dir_normalized
    
    # Reflected point
    reflected_point = line_start + 2 * projection - point_vector
    
    return reflected_point

# Deflate a fat rhombus into smaller tiles
def inflate_fat_rhombus(fat_rhombus):
    A, B, D, C= fat_rhombus[:4]  # Unpack vertices
    
    B_prime = A + phi * (B - A)
    
    D_prime_left = reflect_point_over_line(D, B, B_prime)
    
    left_thin_rhombus = np.array([B, D, B_prime, D_prime_left, B])  # Close the shape
    
    C_prime = A + phi * (C - A)
    
    D_prime_right = reflect_point_over_line(D, C, C_prime)
    
    right_thin_rhombus = np.array([C, D, C_prime, D_prime_right, C])  # Close the shape
    
    E = rotate_point(B, D, angle_144)
    F = rotate_point(D, B_prime, -angle_72)
    G = rotate_point(D, C_prime, angle_72)
    left_thick_rhombus = np.array([B_prime,D,E,F])
    right_thick_rhombus = np.array([C_prime,D,E,G])
    

    return  [fat_rhombus, left_thin_rhombus, right_thin_rhombus, left_thick_rhombus, right_thick_rhombus]

def inflate_thin_rhombus(thin_rhombus):
    A, B, C, D= thin_rhombus[:4]
    D_prime = rotate_point(C,D,angle_72)
    C_prime = rotate_point(C,D,angle_36)
    A_prime = rotate_point(A,D,-angle_36)
    C_prime_prime = rotate_point(D,C_prime, -angle_144)
    A_prime_prime = rotate_point(D, A_prime, angle_144)
    C_left_initial = rotate_point(C_prime, D, -angle_36)
    C_left = C_left_initial * phi
    A_right_initial =  rotate_point(A_prime, D, angle_36)
    A_right = A_right_initial * phi
    E = rotate_point(D_prime, D, angle_108)
    F = rotate_point(D_prime, D, -angle_108)

    left_thin_rhombus = np.array([D, D_prime, C_prime_prime, C_prime, D])  # Added D
    right_thin_rhombus = np.array([D, D_prime, A_prime_prime, A_prime, D])  # Added D
    left_thick_rhombus = np.array([D, C_prime, C_left, E, D])  # Added D
    right_thick_rhombus = np.array([D, A_prime, A_right, F, D])  # Added D
    return [left_thin_rhombus, right_thin_rhombus, left_thick_rhombus, right_thick_rhombus]
def rotate_point(point, center, angle):
    x, y = point
    m, n = center
    x_seg = x - m
    y_seg = y - n

    rotated_x = x_seg * np.cos(angle) - y_seg * np.sin(angle)
    rotated_y = x_seg * np.sin(angle) + y_seg * np.cos(angle)

    x_final = rotated_x + m
    y_final = rotated_y + n
    
    return np.array([x_final, y_final])

def rotate_tile(tile, angle):
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)]
    ])
    return np.dot(tile, rotation_matrix)

# Global variables
current_iteration = 0
star = []
i = 0
# Create the initial star shape
def create_star_shape():
    global star
    global current_iteration
    global i
    while i < 5:
        angle = 2 * np.pi * i / 5  # 72 degrees in radians
        rotated_kite = rotate_tile(fat_rhombus, angle)
        star.append(rotated_kite)
        i += 1
    current_iteration +=1
    return star
    

# Function to check if a tile is a fat rhombus
def is_fat_rhombus(tile):
    side_lengths = [
        np.linalg.norm(tile[1] - tile[0]),  
        np.linalg.norm(tile[2] - tile[1]),  
        np.linalg.norm(tile[3] - tile[2]),  
        np.linalg.norm(tile[0] - tile[3])   
    ]
    
    vectors = [
        tile[1] - tile[0],  
        tile[2] - tile[1],  
        tile[3] - tile[2],  
        tile[0] - tile[3]   
    ]
    angles = [
        np.arccos(np.clip(np.dot(vectors[0], -vectors[3]) / (np.linalg.norm(vectors[0]) * np.linalg.norm(vectors[3])), -1, 1)),  
        np.arccos(np.clip(np.dot(vectors[1], -vectors[0]) / (np.linalg.norm(vectors[1]) * np.linalg.norm(vectors[0])), -1, 1)),  
        np.arccos(np.clip(np.dot(vectors[2], -vectors[1]) / (np.linalg.norm(vectors[2]) * np.linalg.norm(vectors[1])), -1, 1)),  
        np.arccos(np.clip(np.dot(vectors[3], -vectors[2]) / (np.linalg.norm(vectors[3]) * np.linalg.norm(vectors[2])), -1, 1))   
    ]
    
    fat_rhombus_side_length = np.linalg.norm(fat_rhombus[1] - fat_rhombus[0])
    fat_rhombus_angles = [np.pi * 2 / 5, np.pi * 3 / 5, np.pi * 2 / 5, np.pi * 3 / 5]  # 72° and 108° 
    
    tolerance = 1e-6
    side_lengths_match = all(abs(length - fat_rhombus_side_length) < tolerance for length in side_lengths)
    angles_match = all(abs(angle - expected_angle) < tolerance for angle, expected_angle in zip(angles, fat_rhombus_angles))
    
    return side_lengths_match and angles_match

def update_plot(event):
    global current_iteration
    global star

    # Initial generation of the star
    if current_iteration == 0:
        create_star_shape()  # Populate the initial star
    else:
        new_tiles = []
        for tile in star:
            if is_fat_rhombus(tile):
                new_tiles.extend(inflate_fat_rhombus(tile))
            else:
                new_tiles.extend(inflate_thin_rhombus(tile))
        
        # Replace old tiles with newly inflated ones
        star = new_tiles

    # Update the plot
    ax.clear()
    for tile in star:
        if is_fat_rhombus(tile):
            ax.fill(tile[:, 0], tile[:, 1], edgecolor='black', color="green", alpha=0.6)
        else:
            ax.fill(tile[:, 0], tile[:, 1], edgecolor='black', color="lightcoral", alpha=0.6)
    
    current_iteration += 1
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect('equal')
    plt.draw()


# Set up the plot
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(bottom=0.2)  # Adjust the plot area to make space for the button

# Add a button
ax_button = plt.axes([0.4, 0.05, 0.2, 0.075])  # Position of the button
button = Button(ax_button, 'Next generation')  # Create the button
button.on_clicked(update_plot)  # Link the button to the update_plot function

# Initial plot
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_aspect('equal')
plt.show()


