import numpy as np
import matplotlib.pyplot as plt
import os

# Load energy data
energy_file = os.path.join("python_output", "energy_vs_time.txt")

# Read the data
data = np.loadtxt(energy_file, skiprows=1)
time = data[:, 0]
energy = data[:, 1]

# Create the plot
plt.figure(figsize=(10, 6))
plt.plot(time, energy, 'b-', linewidth=2, marker='o', markersize=4)
plt.xlabel('Time')
plt.ylabel('Total Energy')
plt.title('SPARC Python Simulation: Total Energy vs Time')
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save the plot
plot_file = os.path.join("python_output", "energy_evolution.png")
plt.savefig(plot_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"Energy evolution plot saved to {plot_file}")

# Calculate energy conservation error
initial_energy = energy[0]
final_energy = energy[-1]
energy_error = abs(final_energy - initial_energy) / initial_energy * 100
print(f"Initial energy: {initial_energy:.6f}")
print(f"Final energy: {final_energy:.6f}")
print(f"Energy conservation error: {energy_error:.6f}%")