import subprocess
import os
import sys

import numpy as np


DEBUG = False
for arg in sys.argv[1:]:
    if arg in ("-d", "--Debug"):
        DEBUG = True

def generate_samples(x, n):
    scale = 0.000005
    return np.random.normal(loc=x, scale=scale, size=n)

# Hyperparameters
GENERATION = 15
population_size = 10
center_A, center_B, center_C, center_D, center_E = 0.000013,0.000023,-0.000008,0.000006,0.000006
A = generate_samples(center_A, population_size)
B = generate_samples(center_B, population_size)
C = generate_samples(center_C, population_size)
D = generate_samples(center_D, population_size)
E = generate_samples(center_E, population_size)


segHeight, segWidth, numSeg = 0.08, 0.04, 8

process = [None] * population_size
outputs = [None] * population_size
errors = [None] * population_size

# Start processes
print("Initializing Processes")
for i in range(population_size):
    print(f"     process {i+1} running...")
    cmd = [sys.executable, 
           "rigid_body.py", 
           "train",
           str(segHeight),
           str(segWidth),
           str(numSeg),
           str(A[i]),
           str(B[i]),
           str(C[i])]
        #    str(D[i]),
        #    str(E[i])]
    process[i] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

for i in range(population_size):
    outputs[i], errors[i] = process[i].communicate()

print("")

print(f"Process     output")
for i in range(population_size):
    print(f"{i}         {outputs[i].split("\n")[-2]}")

if DEBUG:
    for i in range(population_size):
        print({errors[i]})

def parse(output):
    result = 100
    try:
        result = float(output.split("\n")[-2])
    except:
        print('Individual has invalid parameters')
    return result
        

losses = np.array([parse(output) for output in outputs])
sorted_indices = np.argsort(losses)
losses_sorted = losses[sorted_indices]
A_sorted = A[sorted_indices]
B_sorted = B[sorted_indices]
C_sorted = C[sorted_indices]
D_sorted = D[sorted_indices]
E_sorted = E[sorted_indices]


to_dir = "generations_quartic"
os.makedirs(to_dir, exist_ok=True)
file_path = f"{to_dir}/gen_{GENERATION}.csv"
ranks = np.arange(1, len(losses_sorted) + 1)
data = np.column_stack((ranks, losses_sorted, A_sorted, B_sorted, C_sorted, D_sorted, E_sorted))
np.savetxt(file_path, data, delimiter=",", fmt="%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f", 
            header="rank,loss,A,B,C,D,E", comments="")

print(f"Saved sorted data to {file_path}")