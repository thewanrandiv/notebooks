import math
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Initialize 4 quantum qubits and 3 classical bits for measurement
# q0, q1, q2 = counting qubits
# q3 = target qubit
qc = QuantumCircuit(4, 3)

# --- STEP 1: STATE PREPARATION ---
qc.x(3)  # Put target qubit q3 into |1> state
for i in range(3):
    qc.h(i)  # Put counting qubits q0, q1, q2 into superposition

# --- STEP 2: CONTROLLED UNITARY OPERATIONS ---
# Qubit 0 applies U^1 (1 time P(pi/4))
qc.cp(math.pi / 4, 0, 3)

# Qubit 1 applies U^2 (2 times P(pi/4))
qc.cp(math.pi / 4, 1, 3)
qc.cp(math.pi / 4, 1, 3)

# Qubit 2 applies U^4 (4 times P(pi/4))
for _ in range(4):
    qc.cp(math.pi / 4, 2, 3)

qc.barrier()  # Visual separator matching your image

# --- STEP 3: INVERSE QUANTUM FOURIER TRANSFORM (IQFT) ---
# Swap the outer qubits of the counting register
qc.swap(0, 2)

# IQFT steps on q0
qc.h(0)

# IQFT steps on q1
qc.cp(-math.pi / 2, 0, 1)
qc.h(1)

# IQFT steps on q2
qc.cp(-math.pi / 4, 0, 2)
qc.cp(-math.pi / 2, 1, 2)
qc.h(2)

qc.barrier()  # Visual separator matching your image

# --- STEP 4: MEASUREMENT ---
# Measure counting qubits q0, q1, q2 into classical bits 0, 1, 2
qc.measure([0, 1, 2], [0, 1, 2])

# --- STEP 5: DRAW AND SIMULATE ---
# Draw the circuit using matplotlib backend
fig = qc.draw("mpl")
plt.show()

# Run the simulation to see the output
simulator = AerSimulator()
job = simulator.run(qc, shots=1024)
counts = job.result().get_counts()

print("\n--- Simulation Results ---")
print("Measured State (Binary):", counts)
print("This binary string represents the phase 0.001 in binary, which is 1/8 = 0.125!")