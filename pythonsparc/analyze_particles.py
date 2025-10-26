import numpy as np
import matplotlib.pyplot as plt
import os

# Load the particle data
data_file = os.path.join("python_output", "Coulomb_explosion_dt0p001.npy")
data = np.load(data_file, allow_pickle=True)

# Get the final state of particles (last time step)
final_state = data[-1]  # [time, energy, particle_object]
protons = final_state[2]

# Extract particle positions
x = protons.x
y = protons.y
z = protons.z

# Calculate radial positions
r = np.sqrt(x**2 + y**2 + z**2)

# Create plots
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Plot 1: Particle positions in XY plane
axes[0].scatter(x, y, s=0.1, alpha=0.7)
axes[0].set_xlabel('X')
axes[0].set_ylabel('Y')
axes[0].set_title('Particle Positions (XY plane)')
axes[0].grid(True, alpha=0.3)
axes[0].axis('equal')

# Plot 2: Radial distribution
axes[1].hist(r, bins=50, alpha=0.7, edgecolor='black')
axes[1].set_xlabel('Radial Position')
axes[1].set_ylabel('Number of Particles')
axes[1].set_title('Radial Distribution of Particles')

plt.tight_layout()

# Save the plot
plot_file = os.path.join("python_output", "particle_analysis.png")
plt.savefig(plot_file, dpi=300, bbox_inches='tight')
plt.show()

print(f"Particle analysis plot saved to {plot_file}")

# Print some statistics
print(f"Total number of particles: {len(x)}")
print(f"Mean radial position: {np.mean(r):.4f}")
print(f"Standard deviation of radial position: {np.std(r):.4f}")
print(f"Minimum radial position: {np.min(r):.4f}")
print(f"Maximum radial position: {np.max(r):.4f}")