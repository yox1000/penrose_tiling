import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# Define the five unit vectors e_i at multiples of 72 degrees
angles = [0, 72, 144, 216, 288]  # Angles in degrees
vectors = [np.array([np.cos(np.radians(angle)), np.sin(np.radians(angle))]) for angle in angles]


# Function to generate translated parallel lines
def parallel_lines(vector, gamma, num=10, spacing=1):
    lines = []
    perp = np.array([-vector[1], vector[0]])  # Perpendicular vector
    for i in range(-num, num + 1):
        # Translate the line by γ_i * e_i
        point = i * spacing * perp + gamma * perp
        lines.append((point, vector))
    return lines

# Function to determine which box (interval) a point lies in for a family
#THE ISSUE IS JUST DETERMINE BOX, EVERYTHING ELSE IS GOOD
import numpy as np

def find_interval(point, family_vector):
    """
    Finds the interval index for a point in the context of a given line family.

    Parameters:
        point (tuple or list): The (x, y) coordinates of the point.
        family_vector (tuple or list): The (dx, dy) vector representing the line family's direction.

    Returns:
        int: The interval index the point falls into for the given family.
    """
    # Convert inputs to numpy arrays
    point = np.array(point)
    family_vector = np.array(family_vector)

    # Normalize the family vector
    family_vector = family_vector / np.linalg.norm(family_vector)

    # Perpendicular vector to the family direction
    perp_vector = np.array([-family_vector[1], family_vector[0]])

    # Project the point onto the perpendicular vector
    projection = np.dot(point, perp_vector)

    # Compute the interval index
    interval_index = int(np.floor(float(projection)))

    return interval_index


def calculate_region_tuples(intersection_point, intersecting_families, non_intersecting_families, vectors):
    """
    Calculates the region tuples based on the intersection point and families of lines.

    Parameters:
        intersection_point (tuple): The (x, y) coordinates of the intersection point.
        intersecting_families (list): Indices of families that intersect at the point.
        non_intersecting_families (list): Indices of families that do not intersect at the point.
        vectors (list): The list of vectors representing all line families.

    Returns:
        list: A list of region tuples (5-tuples) for the 4 regions around the point.
    """
    region_tuples = []

    # Get the base intervals for the intersecting families
    base_intervals = [
        find_interval(intersection_point, vectors[family]) for family in intersecting_families
    ]

    # Ensure base_intervals has exactly two valid elements
    if len(base_intervals) != 2 or any(interval is None for interval in base_intervals):
        return region_tuples  # Return empty list if intervals are invalid

    # Iterate over the 4 regions
    for region in range(4):
        # Adjust intervals for intersecting families based on region
        adjusted_intervals = [
            base_intervals[0] + (1 if region in [1, 2] else 0),  # Increment for regions 1 and 2
            base_intervals[1] + (1 if region in [2, 3] else 0),  # Increment for regions 2 and 3
        ]

        # Keep intervals constant for non-intersecting families
        constant_intervals = [
            find_interval(intersection_point, vectors[family]) if family < len(vectors) else 0
            for family in non_intersecting_families
        ]

        # Merge intervals into a 5-tuple
        all_intervals = [0] * 5
        for idx, family in enumerate(intersecting_families):
            if isinstance(family, int) and 0 <= family < len(all_intervals):
                all_intervals[family] = adjusted_intervals[idx]
        for idx, family in enumerate(non_intersecting_families):
            if isinstance(family, int) and 0 <= family < len(all_intervals):
                all_intervals[family] = constant_intervals[idx]

        region_tuples.append(all_intervals)

    return region_tuples


# Function to label regions between lines
def label_regions(lines, vector):
    labels = {}
    total_midpoints = len(lines) - 1  # Total number of midpoints
    
    # Ensure there are enough midpoints to cover the range -10 to 10
    if total_midpoints < 19:
        raise ValueError("Not enough midpoints to cover the range -10 to 10. Need at least 21 midpoints.")
    
    for i in range(total_midpoints):
        # Calculate midpoint between consecutive lines
        midpoint = (lines[i][0] + lines[i + 1][0]) / 2  
        
        # Scale i to the range -10 to 10
        label_index = -10 + i  # Directly map i to -10, -9, ..., 10
        
        # Store the label for the midpoint
        labels[tuple(midpoint)] = label_index
        
        # Debugging: Print midpoint and label_index
        #print(f"Midpoint: {midpoint}, Label Index: {label_index}")
    
    return labels

# Initialize lists to store lines, labels, intersections, and region tuples
all_lines = []
all_labels = []
intersections = []
intersection_labels = []
region_tuples = []

# Generate lines and labels for each vector
for vector in vectors:
    gamma = np.random.uniform(-1, 1) 
     # Generate a random translation for the current vector, record it in random_vals
    lines = parallel_lines(vector, gamma)
    labels = label_regions(lines, vector)
    all_lines.append(lines)
    all_labels.append(labels)

# Function to find intersection points of two lines
def intersection_pt(line1, line2):
    p1, v1 = line1
    p2, v2 = line2
    A = np.array([v1, -v2]).T  # Coefficients for the system of equations
    b = p2 - p1
    t, s = np.linalg.solve(A, b)
    intersection_point = p1 + t * v1
    return intersection_point


# Define unit vectors for the 5 directions
unit_vectors = [(np.cos(angle), np.sin(angle)) for angle in angles]

# Function to compute R for a given 5-tuple
def compute_R(five_tuple):
    R = np.array([0.0, 0.0])  # Start with a zero vector
    for e, d in zip(five_tuple, vectors):
        R += e * np.array(d)  # Multiply and accumulate
    return R

# Function to plot polygons
def plot_polygons(intersection_points, regions_per_point, all_lines, all_labels):

    fig, ax = plt.subplots()

    # Plot the lines and their labels
    for lines, labels in zip(all_lines, all_labels):
        for (point, vector) in lines:
            line_length = 10
            start = point - line_length * vector
            end = point + line_length * vector
            ax.plot([start[0], end[0]], [start[1], end[1]], 'k-', lw=0.5)

        for midpoint, label in labels.items():
            ax.text(midpoint[0], midpoint[1], str(label), fontsize=8, ha='center', va='center', color='blue')

    # Plot the intersection points and regions
    for idx, (intersection, regions) in enumerate(zip(intersection_points, regions_per_point)):
        coordinates = [compute_R(region) for region in regions]
        polygon = Polygon(coordinates, closed=True, edgecolor='blue', alpha=0.5)
        ax.add_patch(polygon)
        ax.scatter(*zip(*coordinates), color='red')  # Region vertices

    # Set axes properties
    ax.set_aspect('equal')
    all_coords = [coord for point in intersection_points for coord in point]
    x_coords, y_coords = zip(*all_coords)
    ax.set_xlim(min(x_coords) - 1, max(x_coords) + 1)
    ax.set_ylim(min(y_coords) - 1, max(y_coords) + 1)
    plt.grid(True)
    plt.title("Polygons Around Intersection Points")
    plt.show()


intersection_points = []
regions_per_point = []

for i, lines1 in enumerate(all_lines):
    for j, lines2 in enumerate(all_lines):
        if j > i:
            for idx1, line1 in enumerate(lines1):
                for idx2, line2 in enumerate(lines2):
                    intersection_point = intersection_pt(line1, line2)

                    #Check if intersection pts are in bounds
                    if not((intersection_point[0] < -5) or (intersection_point[0] > 5) or (intersection_point[1] < -5) or (intersection_point[1] > 5)):
                        intersection_points.append(intersection_point)

                        # Identify intersecting and non-intersecting families
                        intersecting_families = [all_lines[i], all_lines[j]]
                        non_intersecting_families = [x for x in range(len(vectors)) if x not in intersecting_families]
                        # Calculate 5-tuples for the regions
                        region_tuples = calculate_region_tuples(intersection_point, intersecting_families, non_intersecting_families)
                        regions_per_point.append(region_tuples)

# Plot polygons
plot_polygons(intersection_points, regions_per_point, all_lines, all_labels)

