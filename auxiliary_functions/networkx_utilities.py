import networkx as nx
#from visualize_1d import visualize_network_with_transit_times_capacities
import matplotlib.pyplot as plt


def create_graph(A, u, tau, alpha=None):
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add edges with transi_ttime and capacity attributes
    for (i, j) in A:
        G.add_edge(i, j, capacity=u[(i, j)], transit_time=tau[(i, j)])
    
    # Assign alpha values from the alpha dictionary as node labels, if provided
    if alpha:
        for node, label in alpha.items():
            G.nodes[node]['alpha'] = label  # Assign the label from alpha
    
    return G


def visualize_graph(G, sources=[], sinks=[]):
    pos = nx.spring_layout(G)  # Position nodes using a spring layout for visualization
    
    # Draw the nodes
    #nx.draw_networkx_nodes(G, pos, node_size=700, node_color='skyblue')

    # Draw source nodes in green
    nx.draw_networkx_nodes(G, pos, nodelist=sources, node_size=800, node_color='lightgreen')
    
    # Draw sink nodes in red
    nx.draw_networkx_nodes(G, pos, nodelist=sinks, node_size=800, node_color='red')
    
    # Draw the remaining nodes in skyblue
    other_nodes = set(G.nodes()) - set(sources) - set(sinks)
    nx.draw_networkx_nodes(G, pos, nodelist=list(other_nodes), node_size=800, node_color='skyblue')

    # Draw the edges
    nx.draw_networkx_edges(G, pos, arrowstyle='-|>', arrowsize=20, edge_color='black', width=1.5)
    
    # Draw node labels
    node_labels = {node: f"{node}\nα={data['alpha']}" if 'alpha' in data else f"{node}"
                   for node, data in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12, font_color='black')
    
    # Draw edge labels for cost and constraint
    edge_labels = {(i, j): f"u={data['capacity']}, τ={data['transit_time']}"
                   for i, j, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10, font_color='red')
    
    # Display the graph
    plt.title("Network with Min-Cut-Labels α")
    plt.axis('off')  # Hide axes
    plt.show()


# # Example usage of creating a graph:
# A = [(1, 2), (1, 3), (2, 4), (3, 4)]  # Arcs in the network
# u = {(1, 2): 1, (1, 3): 2, (2, 4): 1, (3, 4): 1}  # Cost for each arc in the objective
# tau = {(1, 2): 3, (1, 3): 1, (2, 4): 2, (3, 4): 3}  # Right-hand side values for each arc constraint
# S_plus_X = [1]  # Nodes in S+ ∩ X where α should be 0
# S_minus_X = [4]  # Nodes in S- \ X where α should be T
# T = 4  # The value of T

# # Create the graph
# G = create_graph(A, u, tau)

# # Output the edges and node attributes for verification
# print("Edges with attributes:")
# for edge in G.edges(data=True):
#     print(edge)

# print("\nNodes with attributes:")
# for node in G.nodes(data=True):
#     print(node)

# # Example usage with the previous graph G
# visualize_graph(G, S_plus_X, S_minus_X)

