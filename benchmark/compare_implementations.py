"""
Compare Python and C++ SPARC implementations
"""
import numpy as np
import matplotlib.pyplot as plt

# Read Python results
python_energy_file = "pythonsparc/python_output/energy_vs_time.txt"
python_data = np.loadtxt(python_energy_file, skiprows=1)
python_time = python_data[:, 0]
python_energy = python_data[:, 1]

# Read C++ results
cpp_energy_file = "output/simulation_output_electron.txt"
cpp_data = np.loadtxt(cpp_energy_file, delimiter=',', skiprows=1)
cpp_time = cpp_data[:, 0]
cpp_energy = cpp_data[:, 1]
cpp_max_r2 = cpp_data[:, 2]
cpp_num_particles = cpp_data[:, 3]

print("=" * 80)
print("SPARC Implementation Comparison: Python vs C++")
print("=" * 80)

print("\n### SIMULATION PARAMETERS ###")
print(f"Python - Number of particles: ~10000 (from main.py)")
print(f"C++ - Number of particles from output: {int(cpp_num_particles[0])}")

print("\n### INITIAL CONDITIONS ###")
print(f"Python - Initial Energy: {python_energy[0]:.6e}")
print(f"C++ - Initial Energy: {cpp_energy[0]:.6e}")
print(f"Energy Ratio (C++/Python): {cpp_energy[0]/python_energy[0]:.6e}")

print("\n### FINAL CONDITIONS (t=0.9s) ###")
print(f"Python - Final Energy: {python_energy[-1]:.6e}")
print(f"C++ - Final Energy: {cpp_energy[-1]:.6e}")
print(f"Energy Ratio (C++/Python): {cpp_energy[-1]/python_energy[-1]:.6e}")

print("\n### ENERGY CONSERVATION ###")
python_energy_change = (python_energy[-1] - python_energy[0]) / python_energy[0] * 100
cpp_energy_change = (cpp_energy[-1] - cpp_energy[0]) / cpp_energy[0] * 100
print(f"Python - Energy change: {python_energy_change:.6f}%")
print(f"C++ - Energy change: {cpp_energy_change:.6f}%")

print("\n### ANALYSIS ###")
# Check if the results are scaled versions of each other
normalized_python = (python_energy - python_energy[0]) / python_energy[0]
normalized_cpp = (cpp_energy - cpp_energy[0]) / cpp_energy[0]

max_relative_diff = np.max(np.abs(normalized_python - normalized_cpp))
print(f"Maximum relative difference in normalized energy: {max_relative_diff:.6e}")

if max_relative_diff < 1e-6:
    print("✓ Results show IDENTICAL relative energy evolution")
    print("  The implementations produce the same physics!")
elif max_relative_diff < 1e-3:
    print("~ Results show SIMILAR relative energy evolution")
    print("  Minor differences in implementation or numerics")
else:
    print("✗ Results show DIFFERENT relative energy evolution")
    print("  Significant differences in implementation!")

# Check absolute energy scaling
energy_scale_factor = cpp_energy[0] / python_energy[0]
print(f"\nEnergy scale factor (C++/Python): {energy_scale_factor:.6e}")

# This suggests there's a difference in units or normalization
if abs(energy_scale_factor - 1.0) > 1e-6:
    print("⚠ WARNING: The absolute energy values differ by a large factor!")
    print("  This suggests different normalization or units are being used.")
    print("  Possible causes:")
    print("  - Different number of particles")
    print("  - Different charge normalization")
    print("  - Different mass values")
    print("  - Different physical constants")

# Create comparison plots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Absolute energy vs time
axes[0, 0].plot(python_time, python_energy, 'b-', label='Python', linewidth=2)
axes[0, 0].plot(cpp_time, cpp_energy, 'r--', label='C++', linewidth=2)
axes[0, 0].set_xlabel('Time (s)')
axes[0, 0].set_ylabel('Total Energy')
axes[0, 0].set_title('Absolute Energy Comparison')
axes[0, 0].legend()
axes[0, 0].grid(True)

# Plot 2: Normalized energy (relative to initial)
axes[0, 1].plot(python_time, normalized_python, 'b-', label='Python', linewidth=2)
axes[0, 1].plot(cpp_time, normalized_cpp, 'r--', label='C++', linewidth=2)
axes[0, 1].set_xlabel('Time (s)')
axes[0, 1].set_ylabel('(E - E₀) / E₀')
axes[0, 1].set_title('Normalized Energy Evolution')
axes[0, 1].legend()
axes[0, 1].grid(True)

# Plot 3: Energy conservation error
python_error = np.abs((python_energy - python_energy[0]) / python_energy[0]) * 100
cpp_error = np.abs((cpp_energy - cpp_energy[0]) / cpp_energy[0]) * 100
axes[1, 0].plot(python_time, python_error, 'b-', label='Python', linewidth=2)
axes[1, 0].plot(cpp_time, cpp_error, 'r--', label='C++', linewidth=2)
axes[1, 0].set_xlabel('Time (s)')
axes[1, 0].set_ylabel('Energy Error (%)')
axes[1, 0].set_title('Energy Conservation Error')
axes[1, 0].legend()
axes[1, 0].grid(True)

# Plot 4: Difference in normalized energy
axes[1, 1].plot(python_time, np.abs(normalized_python - normalized_cpp), 'g-', linewidth=2)
axes[1, 1].set_xlabel('Time (s)')
axes[1, 1].set_ylabel('|ΔE_normalized|')
axes[1, 1].set_title('Absolute Difference in Normalized Energy')
axes[1, 1].set_yscale('log')
axes[1, 1].grid(True)

plt.tight_layout()
plt.savefig('comparison_python_vs_cpp.png', dpi=150)
print("\n✓ Comparison plot saved to: comparison_python_vs_cpp.png")

print("\n" + "=" * 80)
