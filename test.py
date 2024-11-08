#%%
from auxiliary_functions.networkx_utilities import create_graph, visualize_graph
from auxiliary_functions.generalized_ext_network import aggregate_cut_time_points
from auxiliary_functions.min_cut_LP import min_cut_over_time

# Parameters (these should be defined based on your data)
arcs = [(1, 2), (1, 3), (2, 4), (3, 4)]  # Arcs in the network
capacities = {(1, 2): 1, (1, 3): 2, (2, 4): 1, (3, 4): 1}  # Cost for each arc in the objective
transit_times = {(1, 2): 3, (1, 3): 1, (2, 4): 2, (3, 4): 3}  # Right-hand side values for each arc constraint
S_plus_X = [1]  # Nodes in S+ ∩ X where α should be 0
S_minus_X = [4]  # Nodes in S- \ X where α should be T
time_horizon = 4  # The value of T

# arcs = [(1, 2), (1, 3), (2, 4), (3, 4), (2, 3)]  # Arcs in the network
# capacities = {(1, 2): 1, (1, 3): 1, (2, 4): 1, (3, 4): 2, (2, 3): 2}  # Cost for each arc in the objective
# transit_times = {(1, 2): 1, (1, 3): 1, (2, 4): 1, (3, 4): 1, (2, 3):0}  # Right-hand side values for each arc constraint
# S_plus_X = [1]  # Nodes in S+ ∩ X where α should be 0
# S_minus_X = [4]  # Nodes in S- \ X where α should be T
# time_horizon = 4  # The value of T


# Compute the min cut values 
alpha, _ = min_cut_over_time(arcs, capacities, transit_times, time_horizon, S_plus_X, S_minus_X)

# Create the graph and display the Min-Cut-values
G = create_graph(arcs, capacities, transit_times, alpha=alpha)
visualize_graph(G, S_plus_X, S_minus_X)

#%% 

terminals = [1, 2, 3, 4]
sources = [1]  # Example S+
sinks = [3]  # Example S-


# Compute "interesting" time points, i.e. all time points of cuts over time for different subsets of terminals
time_points = aggregate_cut_time_points(sources, sinks, arcs, capacities, transit_times, time_horizon)
time_points