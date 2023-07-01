from dimod import ConstrainedQuadraticModel, Integer, Binary, ExactCQMSolver
from graph import V
from graph import A as _A

A = (_A * _A.mean()) / _A.max()

# A = np.array([
#     [0, 1, 2, 1],
#     [1, 0, 1, 2],
#     [2, 1, 0, 1],
#     [1, 2, 1, 0],
# ])

# V = {
#     "cx_0": 2,
#     "cx_1": 5,
#     "cx_2": 3,
#     "cx_3": 9,
# }

# Model
cqm = ConstrainedQuadraticModel()


z = [ 1 - 2*Binary(f'z_{i}') for i in range(A.shape[0])]
# z = [Binary(f'z_{i}', ) for i in range(A.shape[0])]


objective_A = 0

for i in range(A.shape[0]):
    for j in range(A.shape[1]):
        if i != j:
            objective_A += ( A[i][j]**2 ) * (1 - (z[i]*z[j])) / 2



# [0 , 1, 0, 0, 1, 0, 1, 1]
# w[i][j] - z[i] z[j]


objective_B = 0

for i in range(A.shape[0]):
    for j in range(A.shape[1]):
        if i < j:
            objective_B += V[f"cx_{i}"] * V[f"cx_{j}"] * z[i] * z[j]

objective = objective_A + (2 * objective_B)

cqm.set_objective(objective)

# Solver
sampler = ExactCQMSolver()
sampleset = sampler.sample_cqm(cqm)

# sampleset.record
print(sampleset)
pass