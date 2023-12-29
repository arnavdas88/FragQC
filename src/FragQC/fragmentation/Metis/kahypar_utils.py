import os

from pathlib import Path
from itertools import compress

import numpy as np
import networkx as nx

import kahypar

def kahypar_cut(graph: nx.MultiDiGraph, num_fragments = 2, edge_weights = None, node_weights = None, imbalance = None, seed = None):
    adjacent_nodes, edge_splits = _graph_to_hmetis( graph=graph )

    ne = len(edge_splits) - 1
    nv = max(adjacent_nodes) + 1

    if edge_weights == None:
        edge_weights = [1] * ne
    
    if node_weights == None:
        node_weights = [1] * nv

    hypergraph = kahypar.Hypergraph(
        num_nodes = nv,
        num_edges = ne,
        index_vector = edge_splits,
        edge_vector = adjacent_nodes,
        edge_weights = (np.array(edge_weights)*100).astype(int).tolist(),
        node_weights = (np.array(node_weights)*100).astype(int).tolist(),
        k = num_fragments,
    )

    context = kahypar.Context()

    config_path = str(Path(__file__).parent / "_cut_kKaHyPar_sea20.ini")
    print(f"[*] Searching for config at `{config_path}`")
    context.loadINIconfiguration(config_path)

    context.setK(num_fragments)

    if isinstance(imbalance, float):
        context.setEpsilon(imbalance)

    context.suppressOutput(True)
    # KaHyPar fixes seed to 42 by default, need to manually sample seed to randomize:
    kahypar_seed = np.random.default_rng(seed).choice(2**15)
    context.setSeed(kahypar_seed)

    kahypar.partition(hypergraph, context)

    cut_edge_mask = [hypergraph.connectivity(e) > 1 for e in hypergraph.edges()]

    # compress() ignores the extra hyperwires at the end if there is any.
    cut_edges = list(compress(graph.edges, cut_edge_mask))

    fragment_sizes = [hypergraph.blockSize(p) for p in range(num_fragments)]
    print(len(fragment_sizes), fragment_sizes)

    bipartition = [ hypergraph.blockID(n) for n in range(nv) ]

    return len(fragment_sizes), bipartition

def _graph_to_hmetis(graph: nx.MultiDiGraph):
    nodes = list(graph.nodes)
    edges = graph.edges(default=True, data=True)

    adj_nodes = [nodes.index(v) for ops in graph.edges(keys=False) for v in ops]
    edge_splits = np.cumsum([0] + [len(e) for e in graph.edges(keys=False)]).tolist()

    return adj_nodes, edge_splits
