import networkx as nx

def static_min_cut(df, v, w, capacity, length, sources, sinks):

    # Step 1: Create a directed graph with capacities and costs
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row[v], row[w], capacity=row[capacity], weight=row[length])

    # Step 2: Specify subsets of source and sink nodes
    # Ensure that the specified nodes exist in the graph
    source_nodes = [node for node in sources if node in G.nodes]
    sink_nodes = [node for node in sinks if node in G.nodes]

    # Step 3: Add a super-source and super-sink to combine specified sources and sinks
    super_source = 'S'
    super_sink = 'T'

    # Add edges from super-source to all specified source nodes with infinite capacity
    for source in source_nodes:
        G.add_edge(super_source, source, capacity=float('inf'),
                #weight=0
                )

    # Add edges from all specified sink nodes to super-sink with infinite capacity
    for sink in sink_nodes:
        G.add_edge(sink, super_sink, capacity=float('inf'), 
                #weight=0
                )

    # Step 4: Compute the minimum cut
    cut_value, (reachable, non_reachable) = nx.minimum_cut(G, super_source, super_sink, capacity=capacity)

    # Step 5: Display results
    print(f"\nMinimum cut value: {cut_value}")
    print('Source side', reachable)
    print('Sink side', non_reachable)

    # extract the cut edges 
    cutset = set()
    for u, nbrs in ((n, G[n]) for n in reachable):
        cutset.update((u, v) for v in nbrs if v in non_reachable)

    print("Edges in the minimum cut:")
    for u, v in cutset:
        print(f"{u} -> {v}: capacity = {G[u][v][capacity]}")
    
    return cut_value, (reachable, non_reachable)

def static_max_flow(df, v, w, capacity, length, sources, sinks):

    # Step 1: Create a directed graph with capacities and costs
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row[v], row[w], capacity=row[capacity], weight=row[length])

    # Step 2: Specify subsets of source and sink nodes
    # Ensure that the specified nodes exist in the graph
    source_nodes = [node for node in sources if node in G.nodes]
    sink_nodes = [node for node in sinks if node in G.nodes]

    # Step 3: Add a super-source and super-sink to combine specified sources and sinks
    super_source = 'S'
    super_sink = 'T'

    # Add edges from super-source to all specified source nodes with infinite capacity
    for source in source_nodes:
        G.add_edge(super_source, source, capacity=float('inf'),
                #weight=0
                )

    # Add edges from all specified sink nodes to super-sink with infinite capacity
    for sink in sink_nodes:
        G.add_edge(sink, super_sink, capacity=float('inf'), 
                #weight=0
                )

    # Step 4: Compute the maximum flow
    flow_value, flow_dict = nx.maximum_flow(G, _s=super_source, _t=super_sink)

    # Step 5: Display results
    # max flow
    print(f"Maximum flow with value: {flow_value}")
    print("Flow distribution:")
    for u, v, data in G.edges(data=True):
        flow = flow_dict.get(u, {}).get(v, 0)
        if flow > 0:
            print(f"{u} -> {v}: flow = {flow}, capacity = {data[capacity]}"
                #, length = {data['weight']}"
                )
            
    return flow_value, flow_dict