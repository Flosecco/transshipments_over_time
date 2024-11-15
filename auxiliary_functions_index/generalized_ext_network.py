from itertools import chain, combinations
from auxiliary_functions_index.min_cut_LP import min_cut_over_time
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
                capacities[(v,w)] = 10000
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

# arcs = [(1, 2), (1, 3), (2, 4), (3, 4)]  # Arcs in the network
# capacities = {(1, 2): 1, (1, 3): 2, (2, 4): 1, (3, 4): 1}  # Cost for each arc in the objective
# transit_times = {(1, 2): 3, (1, 3): 1, (2, 4): 2, (3, 4): 3}  # Right-hand side values for each arc constraint
# time_horizon = 4  # The value of T
# terminals = [1, 2, 3, 4]
# sources = [1]  # Example S+
# sinks = [4]  # Example S-


# # Compute "interesting" time points, i.e. all time points of cuts over time for different subsets of terminals
# time_points = aggregate_cut_time_points(sources, sinks, arcs, capacities, transit_times, time_horizon)