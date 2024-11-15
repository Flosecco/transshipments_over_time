import networkx as nx
import plotly.graph_objects as go

def create_3d_layered_graph_with_fixed_source_sink(graph, layers, source, sink, layout='spring'):
    """
    Creates a 3D layered visualization of a graph with source fixed on the left and sink on the right.
    
    Parameters:
    - graph (networkx.Graph): The base graph structure.
    - layers (int): Number of layers in the graph.
    - source (node): The source node to fix on the left.
    - sink (node): The sink node to fix on the right.
    - layout (str): Layout for positioning nodes (e.g., 'spring' for spring layout).
    
    Returns:
    - fig (plotly.graph_objects.Figure): A 3D plotly figure of the layered graph.
    """
    # Create a base layout for the nodes in 2D (x, y positions)
    if layout == 'spring':
        pos_2d = nx.spring_layout(graph, seed=42)
    elif layout == 'circular':
        pos_2d = nx.circular_layout(graph)
    else:
        raise ValueError("Unsupported layout type. Use 'spring' or 'circular'.")

    # Determine min and max x positions for left and right alignment
    min_x = min(pos[0] for pos in pos_2d.values())
    max_x = max(pos[0] for pos in pos_2d.values())
    
    # Initialize lists to hold node coordinates and edge traces
    node_x, node_y, node_z = [], [], []
    edge_x, edge_y, edge_z = [], [], []

    # Create layers along the z-axis
    layer_distance = 1  # Distance between layers
    for layer in range(layers):
        z_offset = layer * layer_distance
        for node, (x, y) in pos_2d.items():
            # Set fixed x position for source and sink nodes
            if node == source:
                x = min_x - 1  # Place source to the far left
            elif node == sink:
                x = max_x + 1  # Place sink to the far right

            # Append node coordinates with layer offset in z-axis
            node_x.append(x)
            node_y.append(y)
            node_z.append(z_offset)
            
            # Add edges within the same layer (intra-layer edges)
            for neighbor in graph.neighbors(node):
                x0, y0 = pos_2d[node]
                x1, y1 = pos_2d[neighbor]

                # Adjust x-coordinates for source and sink on the edges
                if node == source:
                    x0 = min_x - 1
                elif node == sink:
                    x0 = max_x + 1
                if neighbor == source:
                    x1 = min_x - 1
                elif neighbor == sink:
                    x1 = max_x + 1

                edge_x += [x0, x1, None]  # None for discontinuity in line
                edge_y += [y0, y1, None]
                edge_z += [z_offset, z_offset, None]
        
        # Add edges between layers (inter-layer edges)
        if layer < layers - 1:
            next_z_offset = (layer + 1) * layer_distance
            for node in graph.nodes():
                x, y = pos_2d[node]

                # Adjust x position for source and sink inter-layer edges
                if node == source:
                    x = min_x - 1
                elif node == sink:
                    x = max_x + 1

                # Edge from current layer to the same node in the next layer
                edge_x += [x, x, None]
                edge_y += [y, y, None]
                edge_z += [z_offset, next_z_offset, None]

    # Create edge trace
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',#+'markers',
        
        #marker=dict(symbol='diamond', size=10),
        line=dict(color='gray', width=2),
        hoverinfo='none'
    )
    
    # Create node trace
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        marker=dict(size=8, color='skyblue', line=dict(width=1, color='black')),
        text=list(graph.nodes()),  # Node labels
        textposition="top center",
        hoverinfo='text'
    )
    
    # Set up the 3D figure
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="3D Layered Graph with Fixed Source and Sink",
        scene=dict(
            xaxis=dict(showbackground=False),
            yaxis=dict(showbackground=False),
            zaxis=dict(showbackground=False),
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    return fig

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
fig = create_3d_layered_graph_with_fixed_source_sink(G, layers=5, source=source, sink=sink, layout='spring')
fig.show()
