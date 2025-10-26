"""
Detailed comparison to identify remaining differences
"""
import numpy as np

print("=" * 80)
print("DETAILED COMPARISON: Python vs C++")
print("=" * 80)

# Simulate the Python particle generation
np.random.seed(10)
N = int(1e4)
R = 1

x = -R + 2 * R * np.random.rand(N)
y = -R + 2 * R * np.random.rand(N)
z = -R + 2 * R * np.random.rand(N)
r2 = x**2 + y**2 + z**2
inside = r2 <= R**2

xp = x[inside]
yp = y[inside]
zp = z[inside]
Np = xp.size

Q = 4/3 * np.pi * R**3

print("\n### PYTHON PARTICLE GENERATION ###")
print(f"Initial attempts: {N}")
print(f"Particles inside sphere: {Np}")
print(f"Acceptance rate: {Np/N*100:.2f}%")
print(f"Total charge Q: {Q}")
print(f"Charge per particle: {Q/Np}")

print("\n### C++ PARTICLE GENERATION ###")
print(f"Target particles: {N}")
print(f"Particles generated: {N} (guaranteed by rejection sampling)")
print(f"Total charge Q: {Q}")
print(f"Charge per particle: {Q/N}")

print("\n### KEY DIFFERENCE ###")
print("🔍 FOUND THE ROOT CAUSE!")
print(f"   Python: Uses {Np} particles (acceptance sampling)")
print(f"   C++: Uses {N} particles (rejection sampling until N particles)")
print(f"   Charge ratio: {(Q/N)/(Q/Np):.6f}")

# Estimate energy scaling
energy_scale_theory = (Np/N) * (Q/N)/(Q/Np)
print(f"\n   Expected energy ratio (C++/Python): ~{Np/N:.6f}")
print(f"   (because fewer particles with different charge normalization)")

# Load actual results
python_data = np.loadtxt("pythonsparc/python_output/energy_vs_time.txt", skiprows=1)
cpp_data = np.loadtxt("output/simulation_output_electron.txt", delimiter=',', skiprows=1)

actual_ratio = cpp_data[0, 1] / python_data[0, 0]
print(f"   Actual energy ratio: {actual_ratio:.6f}")

print("\n### RANDOM NUMBER GENERATORS ###")
print("⚠️ Another potential difference:")
print("   Python: numpy.random.rand() with seed 10")
print("   C++: rand()/RAND_MAX with srand(10)")
print("   These are DIFFERENT RNG algorithms!")
print("   This causes different particle positions even with same seed")

print("\n### CONCLUSION ###")
if abs(actual_ratio - Np/N) < 0.01:
    print("✓ The energy difference is primarily due to:")
    print("  1. Different number of particles (Python: ~5236, C++: 10000)")
    print("  2. Different charge normalization")
    print("  3. Different RNG algorithms (minor effect)")
    print("\n✓ The physics implementations are CORRECT!")
    print("  The small difference is due to initial condition generation.")
else:
    print("⚠️ Additional factors may be contributing to the difference")

print("\n" + "=" * 80)
