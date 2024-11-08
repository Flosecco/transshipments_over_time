import networkx as nx
import math

def create_extended_graph(G, X, T):
    """
    Extends the graph G by adding a super-source psi and modifying the graph as per specifications.
    
    Parameters:
    - G: A directed graph (networkx DiGraph) with capacities and travel times on each arc.
    - X: A subset of terminals in G (a set of nodes).
    - T: Time horizon.
    
    Returns:
    - Extended graph (DiGraph) with a super-source psi and modified arcs.
    """
    # Make a copy of the graph to avoid modifying the original
    G_ext = G.copy()
    
    # Define a super-source node psi
    psi = 'psi'
    G_ext.add_node(psi)
    
    # Add arcs from psi to each source in X with infinite capacity and travel time 0
    for node in X:
        if G_ext.in_degree(node) == 0:  # Check if it's a source (no incoming edges)
            G_ext.add_edge(psi, node, capacity=float('inf'), travel_time=0)
    
    # Add arcs from each sink not in X to psi with infinite capacity and travel time -T
    for node in G_ext.nodes:
        if G_ext.out_degree(node) == 0 and node not in X:  # Check if it's a sink (no outgoing edges)
            G_ext.add_edge(node, psi, capacity=float('inf'), travel_time=-T)
    
    return G_ext

def min_cost_circulation(G):
    """
    Computes the minimum cost circulation in a directed graph G.
    Travel times are interpreted as costs in the min-cost circulation computation.
    
    Parameters:
    - G: A directed graph (networkx DiGraph) with capacities and travel times as costs on each arc.
    
    Returns:
    - cost: The minimum cost of circulation.
    - flow_dict: The flow assignment for each edge in the minimum-cost circulation.
    """
    # Create a copy of the graph to use travel times as costs
    G_cost = G.copy()
    for u, v, data in G_cost.edges(data=True):
        # Interpret travel time as cost
        data['cost'] = data['travel_time']
    
    # Calculate min-cost circulation using NetworkX's min_cost_flow function
    try:
        flow_dict = nx.min_cost_flow(G_cost, capacity='capacity', weight='cost')
        # Calculate the total cost of the circulation
        cost = nx.cost_of_flow(G_cost, flow_dict, weight='cost')
        return cost, flow_dict
    except nx.NetworkXUnfeasible:
        print("The graph does not have a feasible circulation.")
        return None, None

# Example usage
# G = nx.DiGraph()
# G.add_edge('s1', 'v1', capacity=10, travel_time=5)
# G.add_edge('v1', 't1', capacity=15, travel_time=3)
# G.add_edge('s2', 'v2', capacity=10, travel_time=2)
# G.add_edge('v2', 't2', capacity=20, travel_time=4)
# G.add_edge('t1', 't2', capacity=25, travel_time=6)
# X = {'s1', 's2', 't1'}  # Example subset of terminals
# T = 10

# G_ext = create_extended_graph(G, X, T)
# min_cost, flow = min_cost_circulation(G_ext)
# print("Minimum Cost:", min_cost)
# print("Flow Dict:", flow)
