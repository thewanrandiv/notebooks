import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

def build_period_finding_circuit():
    """Builds the 3^x mod 4 period finding circuit."""
    num_counting = 2
    num_target = 2
    
    qc = QuantumCircuit(num_counting + num_target, num_counting)
    
    # Initialization: target to |1> (q2=1, q3=0)
    qc.x(2)
    for qubit in range(num_counting):
        qc.h(qubit)
    qc.barrier()
    
    # Modular Exponentiation Oracle
    qc.cx(0, 3)
    qc.barrier()
    
    # Inverse QFT
    iqft = QFT(num_qubits=num_counting, do_swaps=True).inverse()
    qc.append(iqft, range(num_counting))
    qc.barrier()
    
    # Measurement
    qc.measure(range(num_counting), range(num_counting))
    return qc

# 1. Build and Compile
qc = build_period_finding_circuit()
simulator = AerSimulator()
compiled_qc = transpile(qc, simulator)

# 2. Execute on the Aer Simulator
job = simulator.run(compiled_qc, shots=1024)
counts = job.result().get_counts()

print("=========================================")
print("  PERIOD FINDING EXPERIMENT RESULTS      ")
print("=========================================")
print(f"Raw Measurement Counts: {counts}\n")

# 3. Generate Visualizations

# Draw the circuit safely without forcing Matplotlib figure attributes
circuit_fig = qc.decompose().draw(output="mpl", style="iqp")

# Create a histogram of the probability distribution
hist_fig = plot_histogram(
    counts, 
    title="Measurement Probabilities (Period r=2)", 
    color="midnightblue",
    figsize=(8, 6)
)

# 4. Display the figures (If not using Jupyter, this opens the windows)
plt.show()