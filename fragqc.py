import random
import numpy as np
from graph import E as EDGES
from graph import A, V, mapping_i2n, mapping_n2i

VERTICES = list(V.values())

# FragQC

def cut_size_calculator(partition_vector, edges):
    '''
    partitionVector is ’0’ or ’1’ for vertices (v_1, v_2, .. v_N ) in
    Partition1 or Partition2 respectively, edge e_{k,l} have end points
    v_k and v_l, edgeWeight is the weight of each edge
    '''
    cutSize = 0
    # for i, val in enumerate(partition_vector):
    #     partition_vector[i] = -1 if val is 0 else 1
    # CHECK: if logic matches...
    # for (i_, j_, e) in edges : # while edges != None # We have considered all the edges
    #     i = mapping_n2i[i_]
    #     j = mapping_n2i[j_]
    #     # [ 1, 0 ], 0, 0, 0, 0, 0, 0
    #     cutSize = e * ( partition_vector[i] - partition_vector[j] ) ** 2
    N = A.shape[0]
    for i in range(0, N - 1):
        for j in range(i + 1, N):
            cut_size_update = A[i][j] * (partition_vector[i] - partition_vector[j])**2
            cutSize += cut_size_update
    return cutSize

def cost_calculation(partition_vector, vertex_weight, N):
    weight_p2 = 0
    total_weight = 0
    # FIXME: Total Weight referenced befored assignment
    for i in range(0, N):
        total_weight += vertex_weight[i]
        weight_p2 = weight_p2 + vertex_weight[i] * partition_vector[i]

    weight_p1 = total_weight - weight_p2
    cost = cut_size_calculator(partition_vector, EDGES) * ( (1/weight_p1) + (1/weight_p2) ) # FIXME: edges, edge_weight
    return cost

def mixing_algorithm(vector_a, vector_b):
    assert len(vector_a) == len(vector_b)

    size = len(vector_a)
    partition = random.randint(1, size)
    # print(partition)

    if bool(random.getrandbits(1)):
        return vector_a[0:partition] + vector_b[partition:]
    else:
        return vector_b[0:partition] + vector_a[partition:]

def error_balanced_mincut_finding_algorithm(N, initial_parting_vector, minima_iteration_threshold = 256):
    min_partition_vector = None
    min_cost = cost_calculation(initial_parting_vector, VERTICES, N) # FIXME: vertex_weight
    partition_vector = initial_parting_vector
    cost = [ 99999999, ] * N

    cost_flag = 0

    while cost_flag < minima_iteration_threshold:
        for i in range(0, N):
            partition_vector[i] = np.bitwise_xor(initial_parting_vector[i] , 1)
            cost[i] = cost_calculation(partition_vector, VERTICES, N)
            if cost[i] < min_cost :
                min_cost = cost[i]
                min_partition_vector = partition_vector
                cost_flag = 0
            else:
                cost_flag += 1
        initial_parting_vector = mixing_algorithm(min_partition_vector, initial_parting_vector)


    return min_partition_vector, min_cost