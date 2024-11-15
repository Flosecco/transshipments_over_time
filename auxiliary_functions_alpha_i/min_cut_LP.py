from gurobipy import Model, GRB

def min_cut_over_time(arcs, capacities, transit_times, T, S_plus_X, S_minus_X):

    # Extend the nerwork with the supersource psi and connecting arcs to S_plus_X and from S_minus_X 
    # Make copies to not change the original arcs, capacities and transit_times
    A, u, tau = arcs.copy(), capacities.copy(), transit_times.copy()

    for s in S_plus_X:
        A += [('psi',s)]
        u[('psi',s)] = 10000  # capacity = infitity
        tau[('psi',s)] = 0

    for t in S_minus_X:
        A += [(t,'psi')]
        u[(t,'psi')] = 10000  # capacity = infitity
        tau[(t,'psi')] = -T

    # Create a new model
    model = Model("LP_Model")

    # Variables
    y = model.addVars(A, lb=0, name="y")  # y_a >= 0 for each a in A
    alpha = model.addVars({v for a in A for v in a}, name="alpha")  # α_v for each node in arcs

    # Objective function: Minimize sum of u_a * y_a
    model.setObjective(sum(u[a] * y[a] for a in A), GRB.MINIMIZE)

    # Constraints
    # Constraint: y_a + α_v - α_w >= -τ_a for each arc a = (v, w)
    for a in A:
        v, w = a
        model.addConstr(y[a] + alpha[v] - alpha[w] >= -tau[a], name=f"constraint_{a}")

    # Constraint: α_s = 0 for all s in S+ ∩ X
    for s in S_plus_X:
        model.addConstr(alpha[s] == 0, name=f"alpha_{s}_S_plus_X")

    # Constraint: α_s = T for all s in S- \ X
    for s in S_minus_X:
        model.addConstr(alpha[s] == T, name=f"alpha_{s}_S_minus_X")

    # Optimize the model
    model.optimize()

    # Output the results
    if model.status == GRB.OPTIMAL:
        print("Optimal objective value:", model.objVal)
        for a in A:
            print(f"y[{a}] =", y[a].x)
        for v in alpha:
            print(f"alpha[{v}] =", alpha[v].x)
    else:
        print("No optimal solution found.")
    
    # Remove 'psi' from alpha since psi was only an quxillary node
    if alpha and 'psi' in alpha:
        del alpha['psi']
    
    # Transform Gurobi variable alpha into dictionary
    alpha_dict = {}
    for a in alpha:
        alpha_dict[a] = int(alpha[a].x)  # Access the variable's name and its solution value

    return alpha_dict, y


# # Parameters (these should be defined based on your data)
# arcs = [(1, 2), (1, 3), (2, 4), (3, 4)]  # Arcs in the network
# capacities = {(1, 2): 1, (1, 3): 2, (2, 4): 1, (3, 4): 1}  # Cost for each arc in the objective
# transit_times = {(1, 2): 3, (1, 3): 1, (2, 4): 2, (3, 4): 3}  # Right-hand side values for each arc constraint
# S_plus_X = [1]  # Nodes in S+ ∩ X where α should be 0
# S_minus_X = [4]  # Nodes in S- \ X where α should be T
# time_horizon = 4  # The value of T

# arcs = [(1, 2), (1, 3), (2, 4), (3, 4), (2, 3)]  # Arcs in the network
# capacities = {(1, 2): 1, (1, 3): 1, (2, 4): 1, (3, 4): 2, (2, 3): 2}  # Cost for each arc in the objective
# transit_times = {(1, 2): 1, (1, 3): 1, (2, 4): 1, (3, 4): 1, (2, 3):0}  # Right-hand side values for each arc constraint
# S_plus_X = [1]  # Nodes in S+ ∩ X where α should be 0
# S_minus_X = [4]  # Nodes in S- \ X where α should be T
# time_horizon = 4  # The value of T


# # Compute the min cut values 
# alpha, _ = min_cut_over_time(arcs, capacities, transit_times, time_horizon, S_plus_X, S_minus_X)