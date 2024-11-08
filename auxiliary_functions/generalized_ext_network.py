from itertools import chain, combinations
from auxiliary_functions.min_cut_LP import min_cut_over_time

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
    tuple: A tuple containing:
        - A_inf (list): List of arc tuples representing edges between each node's consecutive time points.
        - capacities (dict): Dictionary with arc tuples as keys and default capacity values (10000) as values.
        - lengths (dict): Dictionary with arc tuples as keys and calculated lengths (difference between consecutive time layers) as values.
    """
    
    A_inf = []
    capacities = {}
    lengths = {}
    for node in nodes:
        for i in range(len(time_points) - 1):
            v = f'{node}^{time_points[i]}'
            w = f'{node}^{time_points[i+1]}'
            A_inf.append((v,w))
            capacities[(v,w)] = 10000
            lengths[(v,w)] = time_points[i+1] - time_points[i]
    return A_inf, capacities, lengths

# arcs = [(1, 2), (1, 3), (2, 4), (3, 4)]  # Arcs in the network
# capacities = {(1, 2): 1, (1, 3): 2, (2, 4): 1, (3, 4): 1}  # Cost for each arc in the objective
# transit_times = {(1, 2): 3, (1, 3): 1, (2, 4): 2, (3, 4): 3}  # Right-hand side values for each arc constraint
# time_horizon = 4  # The value of T
# terminals = [1, 2, 3, 4]
# sources = [1]  # Example S+
# sinks = [4]  # Example S-


# # Compute "interesting" time points, i.e. all time points of cuts over time for different subsets of terminals
# time_points = aggregate_cut_time_points(sources, sinks, arcs, capacities, transit_times, time_horizon)