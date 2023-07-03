import random

import numpy as np


def cut_size_calculator(A, partition_vector):
    '''
    partitionVector is ’0’ or ’1’ for vertices (v_1, v_2, .. v_N ) in
    Partition1 or Partition2 respectively, edge e_{k,l} have end points
    v_k and v_l, edgeWeight is the weight of each edge
    '''
    cutSize = 0

    N = A.shape[0]
    for i in range(0, N - 1):
        for j in range(i + 1, N):
            cut_size_update = A[i][j] * (partition_vector[i] - partition_vector[j])**2
            cutSize += cut_size_update
    return cutSize

def cost_calculation(A, partition_vector):
    N = A.shape[0]
    weight_p2 = 0
    total_weight = 0
    for i in range(0, N):
        total_weight += A[i, i]
        weight_p2 = weight_p2 + A[i, i] * partition_vector[i]

    weight_p1 = total_weight - weight_p2
    cost = cut_size_calculator(A, partition_vector) * ( (1/weight_p1) + (1/weight_p2) )
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

def error_balanced_mincut_finding_algorithm(A, initial_parting_vector, minima_iteration_threshold = 256, mixing_algorithm = mixing_algorithm):
    N = A.shape[0]

    min_partition_vector = initial_parting_vector.copy()
    min_cost = cost_calculation(A, min_partition_vector)
    cost = [ 99999999, ] * N

    cost_flag = 0

    # Result
    __iteration__ = 0
    __history__ = [ ]

    while cost_flag < minima_iteration_threshold:
        partition_vector = min_partition_vector.copy()
        for i in range(0, N):
            partition_vector[i] = np.bitwise_xor(partition_vector.copy()[i] , 1)

            if len(set(partition_vector)) == 1:
                # Skip everythong if all nodes fall in the same bucket
                cost_flag += 1
                continue


            cost[i] = cost_calculation(A, partition_vector)
            # print( partition_vector, cost[i] )
            if cost[i] < min_cost :
                min_cost = cost[i]
                min_partition_vector = partition_vector.copy()
                cost_flag = 0
            else:
                cost_flag += 1

            __history__.append({
                "cost": cost,
                "min-cost": min(cost),
                "avg-cost": sum(cost[:i+1]) / len(cost[:i+1]),
                "partition_vector": partition_vector,
                "min_partition_vector": min_partition_vector,
            })

        __iteration__ += 1
        initial_parting_vector = mixing_algorithm(min_partition_vector, initial_parting_vector)



    return min_partition_vector, min_cost, {"iteration": __iteration__, "history": __history__, "cost": min_cost, "partition": min_partition_vector}