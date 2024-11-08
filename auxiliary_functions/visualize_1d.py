import networkx as nx
import matplotlib.pyplot as plt

def visualize_network_with_transit_times_capacities(graph, sources, sinks):
    """
    Visualizes a network graph with transit_times and capacities, highlighting source and sink nodes.
    
    Parameters:
    - graph (networkx.Graph): The network to be visualized, with 'transit_time' and 'capacity' attributes on edges.
    - source (nodes): The source nodes in the network.
    - sink (nodes): The sink nodes in the network.
    """
    
    # Set up the layout for the nodes
    pos = nx.spring_layout(graph, seed=42)  # Using spring layout for better visualization
    
    # Draw nodes with specific colors for sources and sinks
    node_colors = []
    for node in graph.nodes():
        if node in sources:
            node_colors.append('green')  # Source nodes in green
        elif node in sinks:
            node_colors.append('red')    # Sink nodes in red
        else:
            node_colors.append('lightblue')  # Other nodes in light blue
            
    # Draw the nodes
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=600, edgecolors='k')
    
    # Draw the edges
    nx.draw_networkx_edges(graph, pos, arrowstyle='-|>', arrowsize=15, edge_color='gray')
    
    # Draw node labels
    nx.draw_networkx_labels(graph, pos, font_size=10, font_color='black')
    
    # Prepare edge labels with transit_times and capacities
    edge_labels = {}
    for u, v, data in graph.edges(data=True):
        transit_time = data.get('transit_time', '-')
        capacity = data.get('capacity', '-')
        edge_labels[(u, v)] = f'tau:{transit_time}, c:{capacity}'
    
    # Draw edge labels (transit_times and capacities)
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='blue', font_size=9)
    
    # Set up the plot with a title
    plt.title("Network Visualization with transit_times and Capacities")
    plt.axis("off")  # Hide the axes
    plt.show()

# # Example Usage
# # Define a simple graph with transit_times and capacities for testing the visualization
# G = nx.DiGraph()
# G.add_edge('s', 'b', transit_time=5, capacity=15)
# G.add_edge('s', 'c', transit_time=3, capacity=10)
# G.add_edge('b', 'c', transit_time=2, capacity=20)
# G.add_edge('b', 't', transit_time=4, capacity=10)
# G.add_edge('c', 't', transit_time=1, capacity=25)

# # Define source and sink nodes
# sources = ['s']
# sinks = ['t']

# # Visualize the network
# visualize_network_with_transit_times_capacities(G, sources, sinks)
