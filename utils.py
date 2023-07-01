def get_weighted_edges(graph):
    edge_data = graph.edges(data=True)
    return [(a, b, d['weight']) for (a, b, d) in edge_data]