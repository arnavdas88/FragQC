import numpy as np

import matplotlib.pyplot as plt

from utils import get_weighted_edges
from graph import G, A
from fragqc import error_balanced_mincut_finding_algorithm

# error_balanced_mincut_finding_algorithm(A.shape[0], [1, 0, ]*4)
print(
    error_balanced_mincut_finding_algorithm(A.shape[0], [1, 0, 0, 0, 0, 0, 0, 0, ])
)