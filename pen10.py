import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
from matplotlib.widgets import Button  # Import the Button class
import math

# Initialize Plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect('equal')  # Ensure equal aspect ratio

# Global variables (Initialize empty)
vertices_table = {}  
current_vertex_index = 0
tiles = []
rotation_state = 0
vertex_connections = {}
retired_vertices = {0:0}

# Display vertices in a table with scrollbar, 'Tiled Angle', and 'Connections' columns
table_window = None  # Ensure this is at the top level

def display_vertices_table():
    """Displays the vertices table in a separate, resizable Tkinter window."""

    global table_window # Declare as global
    if table_window and tk.Toplevel.winfo_exists(table_window):  #Check if window exists
        for widget in table_window.winfo_children():
            widget.destroy()   # Clear existing widgets if the table exists
    else:

        table_window = tk.Toplevel()
        table_window.title("Vertices Table")
        table_window.geometry("500x400")  # Set initial size (adjust as needed)

    # Define columns
    columns = ('Index', 'X', 'Y', 'Status', 'Tiled Angle', 'Connections')
    tree = ttk.Treeview(table_window, columns=columns, show='headings', height=15) #Set ttk.Treeview object
    
    # Set column headings
    tree.heading('Index', text='Index')
    tree.heading('X', text='X')
    tree.heading('Y', text='Y')
    tree.heading('Status', text='Status')
    tree.heading('Tiled Angle', text='Tiled Angle')
    tree.heading('Connections', text='Connections')  # Added "Connections" column

    # Insert vertex data (empty initially)
    # ... (we'll add the logic to populate this later)


    # Add a scrollbar
    scrollbar = ttk.Scrollbar(table_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)  # Link scrollbar to the Treeview widget.
    scrollbar.pack(side="right", fill="y") # Correct placement
    tree.pack(side="left", fill="both", expand=True)
    table_window.update_idletasks()


# Call display_vertices_table to create the empty table initially
display_vertices_table() # Call after definition

# Button setup (Create the button after creating the plot)
ax_button = plt.axes([0.7, 0.05, 0.2, 0.075])
button = Button(ax_button, 'Add Tile')

# ... (button click handler will be added later)

plt.show()