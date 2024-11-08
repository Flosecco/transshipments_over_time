import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_3d_layered_graph_with_fixed_source_sink(graph, layers, source, sink, layout='spring'):
    """
    Plots a 3D layered graph in Matplotlib with the source fixed on the left and the sink on the right.
    
    Parameters:
    - graph (networkx.Graph): The base graph structure.
    - layers (int): Number of layers in the graph.
    - source (node): The source node to fix on the left.
    - sink (node): The sink node to fix on the right.
    - layout (str): Layout for positioning nodes (e.g., 'spring' for spring layout).
    """
    # Set up a 2D layout for node positions
    if layout == 'spring':
        pos_2d = nx.spring_layout(graph, seed=42)
    elif layout == 'circular':
        pos_2d = nx.circular_layout(graph)
    else:
        raise ValueError("Unsupported layout type. Use 'spring' or 'circular'.")

    # Determine min and max x positions for left and right alignment
    min_x = min(pos[0] for pos in pos_2d.values())
    max_x = max(pos[0] for pos in pos_2d.values())
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot settings for layer distance and node size
    layer_distance = 1  # Distance between layers
    node_size = 200
    node_colors = []
    
    # Create node positions in 3D
    node_positions = {}
    for layer in range(layers):
        z_offset = layer * layer_distance
        for node, (x, y) in pos_2d.items():
            # Set fixed x position for source and sink nodes
            if node == source:
                x = min_x - 1  # Place source to the far left
                node_color = 'green'
            elif node == sink:
                x = max_x + 1  # Place sink to the far right
                node_color = 'red'
            else:
                node_color = 'skyblue'

            # Save the node's 3D position and color
            node_positions[(node, layer)] = (x, y, z_offset)
            node_colors.append(node_color)
            
            # Draw the node in 3D
            ax.scatter(x, y, z_offset, color=node_color, s=node_size, edgecolor='k')

            # Add a label to the node
            ax.text(x, y, z_offset, s=node, color='black', fontsize=10, ha='center', va='center')
    
    # Draw intra-layer and inter-layer edges
    for layer in range(layers):
        z_offset = layer * layer_distance

        # Intra-layer edges
        for u, v in graph.edges():
            x0, y0, _ = node_positions[(u, layer)]
            x1, y1, _ = node_positions[(v, layer)]
            ax.plot([x0, x1], [y0, y1], [z_offset, z_offset], color="gray", linewidth=1)

        # Inter-layer edges (for connections between layers)
        if layer < layers - 1:
            next_z_offset = (layer + 1) * layer_distance
            for node in graph.nodes():
                x, y, _ = node_positions[(node, layer)]
                x_next, y_next, _ = node_positions[(node, layer)]
                
                # Adjust x position for source and sink inter-layer edges
                if node == source:
                    x = min_x - 1
                elif node == sink:
                    x = max_x + 1

                # Connect the node in this layer to the same node in the next layer
                ax.plot([x, x], [y, y], [z_offset, next_z_offset], color="blue", linewidth=0.5, linestyle='dotted')

    # Set plot limits and labels
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Layer (Z axis)')
    plt.title("3D Layered Graph with Fixed Source and Sink Nodes")

    # Hide grid and axes for a cleaner look
    ax.grid(False)
    ax.set_axis_off()

    plt.show()

# Example Usage
# Create a base graph
G = nx.Graph()
G.add_edges_from([
    ('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D'), ('C', 'D')
])

# Define source and sink nodes
source = 'A'
sink = 'D'

# Visualize the 3D layered graph with fixed source and sink nodes
plot_3d_layered_graph_with_fixed_source_sink(G, layers=3, source=source, sink=sink, layout='spring')
