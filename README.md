# 1 Shor's Period-Finding Subroutine: Code Explanation

This document provides a line-by-line breakdown of the Qiskit implementation used to find the period ($r$) of the modular exponential function:

$$f(x) = 3^x \pmod 4$$

---

## 1. Libraries and Imports

```python
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

```

| Component | Purpose |
| --- | --- |
| `import numpy as np` | Provides mathematical constants (like $\pi$) used for phase rotations. |
| `import matplotlib.pyplot as plt` | The standard Python plotting library used to display the final circuit and graph windows. |
| `from qiskit import ...` | Imports `QuantumCircuit` to build our quantum wires/gates, and `transpile` to translate our high-level logic into instructions a simulator or quantum hardware can actually run. |
| `from qiskit.circuit.library import QFT` | Imports the pre-built Quantum Fourier Transform module, saving us from building complex phase-rotation blocks manually. |
| `from qiskit_aer import AerSimulator` | Imports a high-performance local quantum simulator backend. |
| `from qiskit.visualization import ...` | Imports `plot_histogram` to cleanly chart the probabilities of our measured bitstrings. |

---

## 2. Circuit Architecture Definition

```python
def build_period_finding_circuit():
    num_counting = 2
    num_target = 2

```

* **`num_counting = 2`:** Allocates 2 qubits for the upper "counting" register. This register acts as our timeline/input ($x$). Two qubits allow us to test inputs from $0$ to $3$ ($2^2 = 4$ states).
* **`num_target = 2`:** Allocates 2 qubits for the lower "target" register. This holds the computed result of $3^x \pmod 4$. Since the maximum possible value is $3$ (binary `11`), we need exactly 2 qubits to store it.

```python
    qc = QuantumCircuit(num_counting + num_target, num_counting)

```

* Creates a circuit with 4 total quantum qubits ($2 + 2$) and 2 classical bits (`num_counting`) to store the final measurement answers.

---

## 3. Register Initialization

```python
    qc.x(2)

```

* **`qc.x(2)`:** Flips the first qubit of our target register (`q[2]`) from $|0\rangle$ to $|1\rangle$. Because $3^0 \pmod 4 = 1$, the target register *must* start initialized to the decimal value $1$ (binary `01`).

```python
    for qubit in range(num_counting):
        qc.h(qubit)
    qc.barrier()

```

* Loops through qubits `0` and `1`, applying a **Hadamard (H) gate** to each. This kicks the counting register into a uniform superposition of all possible states ($|00\rangle, |01\rangle, |10\rangle, |11\rangle$).
* **`qc.barrier()`:** Visual separator that forces Qiskit optimization steps to treat the initialization and the core algorithm completely separately.

---

## 4. The Modular Exponentiation Oracle

```python
    qc.cx(0, 3)
    qc.barrier()

```

This single gate calculates the actual math operation ($3^x \pmod 4$).

* When `q[0]` (representing $3^1$) is active, it multiplies our target register ($1$, binary `01`) by $3$, which equals $3$ (binary `11`).
* Notice that shifting from binary `01` to binary `11` only requires flipping the second qubit (`q[3]`). Therefore, a simple **Controlled-NOT (CX)** gate controlled by `q[0]` and targeting `q[3]` achieves this transformation perfectly.
* *Why is there no gate for `q[1]`?* `q[1]` represents $3^2 \pmod 4 = 9 \pmod 4 = 1$. Multiplying a state by $1$ does nothing (it's the identity operation), so we can leave it empty.

---

## 5. The Inverse QFT

```python
    iqft = QFT(num_qubits=num_counting, do_swaps=True).inverse()
    qc.append(iqft, range(num_counting))
    qc.barrier()

```

* **`QFT(...).inverse()`:** Generates a 2-qubit Quantum Fourier Transform block and immediately flips it into its mathematical **inverse**.
* **`qc.append(...)`:** Stitches this Inverse QFT block onto our counting qubits (`q[0]` and `q[1]`). This acts like a prism, turning phase patterns inside our quantum states back into a regular frequency that we can measure.

---

## 6. Measurement

```python
    qc.measure(range(num_counting), range(num_counting))
    return qc

```

* Maps quantum qubits `0` and `1` directly to classical bits `0` and `1`. This forces the superposition to collapse into a concrete binary answer.

---

## 7. Execution and Compilation

```python
qc = build_period_finding_circuit()
simulator = AerSimulator()
compiled_qc = transpile(qc, simulator)

```

* **`qc = build_period_finding_circuit()`:** Calls our function to generate the completed circuit object.
* **`simulator = AerSimulator()`:** Spins up the local simulated quantum hardware.
* **`transpile(qc, simulator)`:** Essential optimization step. It breaks down high-level, abstract pieces (like our `IQFT` object) into basic physical gates that the `AerSimulator` can actually process.

```python
job = simulator.run(compiled_qc, shots=1024)
counts = job.result().get_counts()

```

* **`simulator.run(..., shots=1024)`:** Runs our compiled program 1,024 separate times to gather statistically reliable probability data.
* **`job.result().get_counts()`:** Extracts a dictionary containing our final measurement bitstrings and how many times they occurred.

---

## 8. Data Visualization

```python
circuit_fig = qc.decompose().draw(output="mpl", style="iqp")

```

* **`.decompose()`:** Explodes the high-level macro blocks (like the `IQFT` box) into their raw internal components (Hadamards and Phase gates).
* **`.draw(output="mpl")`:** Renders the layout as a graphical Matplotlib blueprint using modern `iqp` styling.

```python
hist_fig = plot_histogram(counts, title="Measurement Probabilities (Period r=2)", color="midnightblue", figsize=(8, 6))
plt.show()

```

* Takes our output results dictionary and processes it into a clear, dual-peaked bar chart displaying the probabilities of hitting `00` and `10`.
* **`plt.show()`:** Commands Python to render the windows on-screen.



# 2 Comparison of SpinQ vs Qiskit Results

```python
content = """# 3-Qubit Quantum Phase Estimation (QPE) Project

## Project Overview
This project implements a 4-qubit Quantum Phase Estimation (QPE) circuit using IBM's Qiskit framework. QPE is a core quantum subroutine used to estimate the unknown phase (or angle) of a quantum gate. 

In this specific implementation:
* We use **3 counting qubits** to measure and store our final answer.
* We use **1 target qubit** where we apply a specific rotation angle ($45^\\circ$ or $\\pi/4$ radians).
* The algorithm will decode this rotation and output the binary string `001`, which mathematically represents the fraction $1/8$ ($0.125$).

---

## Line-by-Line Code Explanation

Here is exactly what every line of the Python script is doing, written in plain and simple terms:

### 1. Bringing in the Libraries

```

```text
QPE_README.md generated successfully.

```python
import math
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

```

* `import math`: Gives us access to standard math tools, specifically the value of Pi ($\pi$).
* `import matplotlib.pyplot as plt`: A charting library used to physically draw and pop up the quantum circuit diagram on your screen.
* `from qiskit import QuantumCircuit`: Imports the core blueprint tool from Qiskit used to design quantum registers, wires, and gates.
* `from qiskit_aer import AerSimulator`: Imports a high-performance quantum computer simulator that runs directly on your local CPU.

### 2. Setting Up the Circuit Wires

```python
qc = QuantumCircuit(4, 3)

```

* This creates a blank quantum circuit named `qc`.
* The number `4` means we are creating **4 Quantum bits (qubits)** labeled $q_0, q_1, q_2, q_3$.
* The number `3` means we are creating **3 Classical bits** labeled $c_0, c_1, c_2$ to safely store our final measurement numbers.

### 3. State Preparation (Starting Conditions)

```python
qc.x(3)

```

* `qc.x(3)`: Applies a NOT gate (X-gate) to the target qubit ($q_3$). This flips it from its default ground state $|0\rangle$ to the $|1\rangle$ state, which is required for the math of this algorithm to work.

```python
for i in range(3):
    qc.h(i)

```

* This is a quick loop that applies a Hadamard gate (`H`) to qubits $0, 1,$ and $2$.
* The H-gate puts these qubits into **Superposition**—meaning they are now perfectly balanced between being a `0` and a `1` at the exact same time.

### 4. Controlled Phase Gates (The Quantum Math)

```python
qc.cp(math.pi / 4, 0, 3)

```

* `qc.cp(...)`: Applies a Controlled-Phase gate. Qubit $q_0$ acts as the control switch, and qubit $q_3$ is the target.
* `math.pi / 4`: This sets the rotation angle to $\pi/4$ radians, which is exactly $45^\circ$.

```python
qc.cp(math.pi / 4, 1, 3)
qc.cp(math.pi / 4, 1, 3)

```

* Qubit $q_1$ applies the $45^\circ$ gate **two times**, totaling a $90^\circ$ phase shift.

```python
for _ in range(4):
    qc.cp(math.pi / 4, 2, 3)

```

* Qubit $q_2$ applies the $45^\circ$ gate **four times** inside a loop, totaling a $180^\circ$ phase shift. Notice how the rotations double each time ($1 \times, 2 \times, 4 \times$); this matches binary counting!

```python
qc.barrier()

```

* `qc.barrier()`: Draws a grey vertical dashed line on your circuit diagram. It doesn't change the physics; it just keeps your diagram organized into neat sections.

### 5. Reversing the Fourier Transform (Decoding the Answer)

```python
qc.swap(0, 2)

```

* `qc.swap(0, 2)`: Swaps the positions of qubit 0 and qubit 2. This re-orders our binary digits so they read cleanly from left-to-right.

```python
qc.h(0)
qc.cp(-math.pi / 2, 0, 1)
qc.h(1)
qc.cp(-math.pi / 4, 0, 2)
qc.cp(-math.pi / 2, 1, 2)
qc.h(2)

```

* This block is the **Inverse Quantum Fourier Transform (IQFT)**. It uses a mix of negative rotations ($-\pi/2$ and $-\pi/4$) and H-gates to collapse our messy phase angles back into solid, readable binary fractions.

```python
qc.barrier()

```

* Another visual divider line before taking measurements.

### 6. Reading the Results

```python
qc.measure([0, 1, 2], [0, 1, 2])

```

* `qc.measure(...)`: Takes the fuzzy quantum states from counting qubits $q_0, q_1,$ and $q_2$ and forces them to collapse into standard digital numbers (`0` or `1`).
* The results are permanently saved into classical bits $c_0, c_1,$ and $c_2$.

### 7. Drawing and Simulating

```python
fig = qc.draw("mpl")
plt.show()

```

* `qc.draw('mpl')`: Converts your abstract code instructions into a beautiful, color-coded visual schematic using Matplotlib.
* `plt.show()`: Tells your computer operating system to open up a graphical window popping up the image.

```python
simulator = AerSimulator()
job = simulator.run(qc, shots=1024)
counts = job.result().get_counts()

```

* `AerSimulator()`: Boots up a virtual perfect quantum computer inside your CPU.
* `simulator.run(qc, shots=1024)`: Runs your circuit through the simulator exactly $1,024$ times to gather statistical results.
* `counts = ...`: Summarizes the final tally of your outputs.

```python
print("\\n--- Simulation Results ---")
print("Measured State (Binary):", counts)

```

* Prints the final scorecard out to your terminal screen. It will show `{'001': 1024}`, meaning your code successfully found the $45^\circ$ phase!
"""

with open('QPE_README.md', 'w') as f:
f.write(content)

print("QPE_README.md generated successfully.")

```
Your comprehensive `README.md` file for the 4-qubit Quantum Phase Estimation code has been successfully generated. 

[file-tag: code-generated-file-0-1779364941858877133]

### How This Markdown Document is Formatted:

* **Headers (`#`, `##`, `###`)**: Organized into clear reading hierarchies (Project Overview $\rightarrow$ Code Explanations $\rightarrow$ Individual blocks) so that someone reading it on GitHub or a markdown viewer can easily jump between sections.
* **Math Blocks (`$...$`)**: Used to cleanly display formulas like $45^\circ$, $\pi/4$, and $|1\rangle$ states natively without breaking your text styling.
* **Code Blocks (

```