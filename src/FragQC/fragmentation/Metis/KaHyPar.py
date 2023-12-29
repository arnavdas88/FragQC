import random
import networkx as nx

from src.FragQC.Result import Result
from src.FragQC.fragmentation.GeneticAlgorithm.utils import cost_calculation

from src.FragQC.fragmentation.Metis.kahypar_utils import kahypar_cut

from typing import Any, List, Mapping

from dataclasses import dataclass, field

@dataclass
class KaHyParResult:
    cost: float
    num_cuts: float
    partition: List[int] = field()

class KaHyParAlgorithm:
    def __init__(self, ) -> None:
        pass

    def __call__(self, A, ) -> Result:
        graph = nx.from_numpy_matrix(A)
        graph = nx.MultiDiGraph(graph).to_undirected()
        graph_node_weight = A.diagonal().tolist()
        graph_edge_weight = [ e['weight'] for (_, _, e) in graph.edges(data=True)]
        n_cuts, bipartition = kahypar_cut(
            graph = graph,
            node_weights = graph_node_weight,
            edge_weights = graph_edge_weight,
            # seed = 1234
        )
        cost = cost_calculation(A, bipartition)
        result = Result(min_cost = cost, partition = bipartition, raw_results = KaHyParResult(partition=bipartition, num_cuts=n_cuts, cost=cost))

        return result
