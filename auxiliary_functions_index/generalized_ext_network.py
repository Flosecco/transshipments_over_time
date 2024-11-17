from itertools import chain, combinations
from auxiliary_functions_index.min_cut_LP import min_cut_over_time
from auxiliary_functions_index.networkx_utilities import create_graph_from_df, cut_capacity
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

def all_valid_subsets(S_plus, S_minus):
    """
    Generate all subsets X of terminals (=S_plus + S_minus) such that S+ ∩ X and S- \ X are non-empty.

    Parameters:
    - S_plus: List representing S+
    - S_minus: List representing S-

    Returns:
    - List of valid subsets X (as lists)
    """
    # Helper function to generate all subsets of a list
    def all_subsets(lst):
        return chain.from_iterable(combinations(lst, r) for r in range(len(lst) + 1))

    valid_subsets = []
    
    # Set of terminals
    S = S_plus + S_minus

    # Iterate over all subsets of terminals
    for subset in all_subsets(S):
        subset = list(subset)  # Convert tuple to list
        # Check the conditions:
        if any(x in subset for x in S_plus) and any(x not in subset for x in S_minus):
            valid_subsets.append(subset)
    
    return valid_subsets

# # Example usage
# S = [1, 2, 3, 4]
# S_plus = [1, 2]  # Example S+
# S_minus = [3, 4]  # Example S-

# valid_subsets = all_valid_subsets(S, S_plus, S_minus)
# print("Valid subsets:", valid_subsets)


### 
def aggregate_cut_time_points(sources, sinks, arcs, capacities, transit_times, time_horizon):
    """
    Computes and aggregates distinct time points from min-cut calculations over time for various subsets 
    of terminal nodes. Each subset meets the criteria that `sources ∩ X` and `sinks \ X` are non-empty. 

    Parameters:
    - sources (list): A subset of `terminals` representing source nodes (S+).
    - sinks (list): A subset of `terminals` representing sink nodes (S-).

    Returns:
    - list: A sorted list of distinct time points derived from min-cut calculations over subsets of terminals.
    """

    # Compute all subsets of S such that S+ ∩ X and S- \ X non-empty
    valid_subsets = all_valid_subsets(sources, sinks)

    # Compute "interesting" time points, i.e. all time points from the min-cuts over time for differens 
    # subsets of terminals 
    time_points = set()

    # Loop over the different subsets of terminals, compute their min-cut alpha-values and aggreate all time points
    for X in valid_subsets:

        # Compute S+ ∩ X and S- \ X
        S_plus_X = [s for s in sources if s in X]
        S_minus_X = [s for s in sinks if s not in X]

        # Compute alpha-values, i.e. time points of min-cut over time for the designated set X
        alpha, _ = min_cut_over_time(arcs, capacities, transit_times, time_horizon, S_plus_X, S_minus_X)
        
        # Update time_points to include unique values from both time_points and alpha's values 
        time_points = sorted(list(set(time_points) | set(alpha.values())))

        print('\nX:', X)
        print('S+ ∩ X', S_plus_X)
        print('S- \ X:', S_minus_X)
        print('alphas:', set(alpha.values()))

    return time_points


def create_A_inf(nodes, time_points):
    """
    Creates a list of arcs between consecutive time points for each node and assigns capacities and transit times.

    Parameters:
    nodes (list): List of nodes in the network.
    time_points (list): List of time points.

    Returns:
    pd.DataFrame: df with columns:
        - v^i
        - w^j
        - capacity	
        - length	
        - alpha_v	
        - alpha_w	
    """
    
    A_inf = []
    capacities = {}
    lengths = {}
    alpha_v = {}
    alpha_w = {}
    for node in nodes:
        for i, alpha_i in enumerate(time_points, start=1):
            if i < max(time_points):
                v = f'{node}^{i}'
                w = f'{node}^{i+1}'
                A_inf.append((v,w))
                capacities[(v,w)] = float('inf')
                lengths[(v,w)] = 1 # length of (vi,wj) is j - i; vertical arcs between consecutive layers  => length = 1
                alpha_v[(v,w)] = time_points[i]
                alpha_w[(v,w)] = time_points[i+1]

    df_inf = pd.DataFrame({
        'v^i': [arc[0] for arc in A_inf],
        'w^j': [arc[1] for arc in A_inf],
        'capacity': [capacities[arc] for arc in A_inf],
        'length': [lengths[arc] for arc in A_inf],
        'alpha_v':  [alpha_v[arc] for arc in A_inf],
        'alpha_w':  [alpha_w[arc] for arc in A_inf],

    })

    return df_inf

def initialize_A_fin(arcs, time_points, original_capacities, original_transit_times):
    """
    Creates the finite capacity arc set, computes the lengths of the arcs and sets the arc capacities to zero.

    Parameters:
    nodes (list): List of nodes in the network.
    time_points (list): List of time points.

    Returns:
    pd.Dataframe: A df with columns:
        - v^i
        - w^j
        - capacity (dict): Dictionary with arc tuples as keys and default capacity values (10000) as values.
        - length (dict): Dictionary with arc tuples as keys and calculated lengths (difference between consecutive time layers) as values.
        - alpha_v
        - alpha_w
        - original_capacity
        - original_transit_time

    """
    # Initialize the finite capacity arcs with capacity and compute their length
    A_fin = []
    new_capacities = {}
    original_capacities_dict = {}
    original_transit_times_dict = {}
    length = {}
    alpha_v = {}
    alpha_w = {}

    # Loop over arcs and time points to compute the capacity and length for each inter-time-layer arc in the extened network
    for arc in arcs:
        v, w = arc
        for i in range(len(time_points)):
            # Initialize vi which is the i-th copy of the original node v
            vi = f'{v}^{i + 1}'
            for j in range(i,len(time_points)):
                # Initialize wj which is the j-th copy of the original node w
                wj = f'{w}^{j + 1}'
                # add arc vi,wj, compute the length of the arc and initialize the new capacity with 0
                A_fin.append((vi,wj))
                new_capacities[(vi,wj)] = 0
                length[(vi,wj)] = j - i
                original_capacities_dict[(vi,wj)] = original_capacities[v,w]
                original_transit_times_dict[(vi,wj)] = original_transit_times[v,w]
                alpha_v[(vi,wj)] = time_points[i]
                alpha_w[(vi,wj)] = time_points[j]

    #A_fin, new_capacities, lengths_fin, original_capacities, original_transit_times = create_A_fin(arcs, time_points, capacities, transit_times)
    df_fin = pd.DataFrame({
        'v^i': [arc[0] for arc in A_fin],
        'w^j': [arc[1] for arc in A_fin],
        'capacity': [new_capacities[arc] for arc in A_fin],
        'length': [length[arc] for arc in A_fin],
        'alpha_v':  [alpha_v[arc] for arc in A_fin],
        'alpha_w':  [alpha_w[arc] for arc in A_fin],        
        'original_capacity': [original_capacities_dict[arc] for arc in A_fin],
        'original_transit_time': [original_transit_times_dict[arc] for arc in A_fin]
    })

    return df_fin


def get_time_level(strings):
    """
    Extracts the time level (number after the caret '^') from each string in the list.

    Parameters:
    strings (list): List of strings in the form 'node^number'.

    Returns:
    list: List of time levels (numbers) extracted after the caret (^) in each string.
    """
    time_levels = [int(s.split('^')[1]) for s in strings]
    return time_levels


def create_A_fin(arcs, time_points, original_capacities, original_transit_times, index_to_alpha):

    # initalize the finite-capacty arc set with capacity = 0
    df_fin = initialize_A_fin(arcs, time_points, original_capacities, original_transit_times)

    # Compute time level nr (by splitting the node's name at '^' and taking the latter part)
    df_fin['i'] = [int(s.split('^')[1]) for s in df_fin['v^i']] 
    df_fin['j'] = [int(s.split('^')[1]) for s in df_fin['w^j']] 
    

    # Helper function to calculate the capacity for arcs of length zero
    def calculate_capacity_for_length_zero_arcs(row):
        # Set capacities for arcs of length 0, which do not belong to the top layer
        if (row['length'] == 0) and (row['alpha_v']  < max(time_points)):
            # capacity(v^i,w^i) = original_capacity(v,w) * (alpha(i+1) - alpha(i) - transit_time(v,w))
            return max(0, row['original_capacity'] * (index_to_alpha[row['i'] + 1] - row['alpha_v'] - row['original_transit_time']))
        else:
            return row['capacity']  # Or another default value if needed


    # Apply the function row-wise and assign the result to a new column
    df_fin['capacity'] = df_fin.apply(calculate_capacity_for_length_zero_arcs, axis=1) 


    # Compute arc capacites for arc lengths of ell > 0
    # Helper function
    def max_term_for_arcs_of_lenth_at_least_1(row):
        # Access the required alpha values
        alpha_1 = row['alpha_v'] # alpha[i]
        alpha_2 = index_to_alpha[row['i'] + ell + 1] # alpha[i + ell + 1]
        
        # Calculate the max term
        max_term = max(0, row['original_capacity'] * (alpha_2 - alpha_1 - row['original_transit_time']))
        
        return max_term

    #df_fin['window_cap'] = None
    for ell in range(1, len(time_points)): # for ell in {1, 2, | T_tilde | - 1}
        # Loop over the arcs of length ell
        if ell == 2:
            break
        df = df_fin[df_fin['length'] == ell]
        for index, row in df.iterrows():
            # Create networkx graph with current capacities
            graph = create_graph_from_df(df_fin, 'v^i', 'w^j', 'capacity', 'length')
            # For arc (v^i, w^j) get the original node names v,w and the indices i,j
            v, i = row['v^i'].split('^') 
            w, j = row['w^j'].split('^') 
            # leave the capacities for arcs inside and into the top layer unchanged
            if (int(j) < len(time_points)) and (int(i) < len(time_points)):
                print('index : ', index, f"\t arc : ({row['v^i']}, {row['w^j']})")
                # Node sets {v^i, v^{i+1}, ..., v^j} and {w^i, w^{i+1}, ..., w^j}
                V_i_to_j = [f'{v}^{k}' for k in range(int(i), int(j)+1)]
                W_i_to_j = [f'{w}^{k}' for k in range(int(i), int(j)+1)]
                # Compute the capacity of the cut separating V_i_to_j and W_i_to_j 
                window_capacity = cut_capacity(graph, V_i_to_j, W_i_to_j)
                # Compute capacity for current arc
                cap = max_term_for_arcs_of_lenth_at_least_1(row) - window_capacity
                df.at[index, 'capacity'] = cap
                df_fin.at[index, 'capacity'] = cap
                #df_fin.at[index, 'window_cap'] = window_capacity
                print(f"new cap of ({row['v^i']}, {row['w^j']}) = ", cap)

    return df_fin


def plot_GTEN(df, v, w, capacity, length, alpha_v, alpha_w):
    # Create a directed graph
    G = nx.DiGraph()

    # Add edges to the graph along with attributes
    for _, row in df.iterrows():
        G.add_edge(row[v], row[w], capacity=row[capacity], length=row[length])

    # Set node positions based on layers alpha_v and alpha_w
    pos = {}
    layer_gap = 5
    node_gap = 1

    for _, row in df.iterrows():
        x, y = row[v], row[w]  
        pos[x] = (int(x.split('^')[0]) * node_gap, row[alpha_v] * layer_gap)
        pos[y] = (int(y.split('^')[0]) * node_gap, row[alpha_w] * layer_gap)

    # Draw the graph
    plt.figure(figsize=(10, 6))
    nx.draw(
        G, pos,
        with_labels=True,
        node_color='skyblue',
        node_size=1000,
        edge_color='gray',
        arrows=True,
        font_size=10,
    )

    # Add edge labels (capacity or length)
    edge_labels = {(row[v], row[w]): f"u={row[capacity]}\nℓ={row[length]}" for _, row in df.iterrows()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,label_pos=0.4, font_color='red', font_size=9)

    plt.title("Generalized Time-Expanded Graph")
    plt.show()

# arcs = [(1, 2), (1, 3), (2, 4), (3, 4)]  # Arcs in the network
# capacities = {(1, 2): 1, (1, 3): 2, (2, 4): 1, (3, 4): 1}  # Cost for each arc in the objective
# transit_times = {(1, 2): 3, (1, 3): 1, (2, 4): 2, (3, 4): 3}  # Right-hand side values for each arc constraint
# time_horizon = 4  # The value of T
# terminals = [1, 2, 3, 4]
# sources = [1]  # Example S+
# sinks = [4]  # Example S-


# # Compute "interesting" time points, i.e. all time points of cuts over time for different subsets of terminals
# time_points = aggregate_cut_time_points(sources, sinks, arcs, capacities, transit_times, time_horizon)