import networkx as nx

def create_time_expanded_network(G:nx.DiGraph, T:int):
    """
    Creates a time-expanded network from a given directed graph and time horizon.

    Parameters:
    G (networkx.DiGraph): The original directed graph.
    T (int): The time horizon (number of time steps).

    Returns:
    networkx.DiGraph: The time-expanded network as a directed graph.
    """
    # Initialize the time-expanded graph
    expanded_graph = nx.DiGraph()
    
    # Step 1: Create time-expanded nodes for each original node at each time step
    for t in range(T):
        for node in G.nodes():
            expanded_graph.add_node((node, t))
    
    # Step 2: Create edges based on the original graph structure
    # Add transit edges according to the original graph
    for t in range(T - 1):
        for u, v in G.edges():
            expanded_graph.add_edge((u, t), (v, t + 1))
    
    # Step 3: Optionally add waiting edges to allow staying at a node across time steps
    for t in range(T - 1):
        for node in G.nodes():
            expanded_graph.add_edge((node, t), (node, t + 1))
    
    return expanded_graph

G = nx.DiGraph()
G.add_edges_from([(1, 2), (2, 3), (3, 1)])
T = 3
expanded_network = create_time_expanded_network(G, T)


