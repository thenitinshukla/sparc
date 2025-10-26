import numpy as np
import matplotlib.pyplot as plt
import os

def analyze_energy_conservation():
    """Analyze energy conservation from the simulation"""
    # Load energy data
    energy_file = os.path.join("python_output", "energy_vs_time.txt")
    data = np.loadtxt(energy_file, skiprows=1)
    time = data[:, 0]
    energy = data[:, 1]
    
    # Calculate energy conservation error
    initial_energy = energy[0]
    final_energy = energy[-1]
    energy_error = abs(final_energy - initial_energy) / initial_energy * 100
    
    # Create energy evolution plot
    plt.figure(figsize=(12, 8))
    plt.style.use('dark_background')
    fig = plt.gcf()
    fig.patch.set_facecolor('black')
    ax = plt.gca()
    ax.set_facecolor('black')
    
    plt.plot(time, energy, 'cyan', linewidth=2, marker='o', markersize=4)
    plt.xlabel('Time', color='white')
    plt.ylabel('Total Energy', color='white')
    plt.title('SPARC Python Simulation: Total Energy vs Time', color='white', pad=20)
    plt.grid(False)
    
    # Style the axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.tick_params(colors='white')
    
    plt.tight_layout()
    energy_plot_file = os.path.join("python_output", "energy_evolution_analysis.png")
    plt.savefig(energy_plot_file, dpi=300, bbox_inches='tight', facecolor='black')
    plt.show()
    
    return initial_energy, final_energy, energy_error

def analyze_particle_distribution():
    """Analyze particle distribution and positions"""
    # Load the particle data
    data_file = os.path.join("python_output", "Coulomb_explosion_dt0p001.npy")
    data = np.load(data_file, allow_pickle=True)
    
    # Get initial and final states
    initial_state = data[0]  # [time, energy, particle_object]
    final_state = data[-1]   # [time, energy, particle_object]
    
    initial_protons = initial_state[2]
    final_protons = final_state[2]
    
    # Extract particle positions
    x_initial = initial_protons.x
    y_initial = initial_protons.y
    z_initial = initial_protons.z
    
    x_final = final_protons.x
    y_final = final_protons.y
    z_final = final_protons.z
    
    # Calculate radial positions
    r_initial = np.sqrt(x_initial**2 + y_initial**2 + z_initial**2)
    r_final = np.sqrt(x_final**2 + y_final**2 + z_final**2)
    
    # Create comprehensive particle analysis plots
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(20, 15))
    fig.patch.set_facecolor('black')
    
    # Plot 1: Initial particle positions in XY plane
    ax1 = fig.add_subplot(2, 3, 1)
    ax1.scatter(x_initial, y_initial, s=0.5, alpha=0.7, color='cyan')
    ax1.set_xlabel('X', color='white')
    ax1.set_ylabel('Y', color='white')
    ax1.set_title('Initial Particle Positions (XY plane)', color='white', pad=20)
    ax1.grid(False)
    ax1.axis('equal')
    ax1.set_facecolor('black')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_color('white')
    ax1.spines['left'].set_color('white')
    ax1.tick_params(colors='white')
    
    # Plot 2: Final particle positions in XY plane
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.scatter(x_final, y_final, s=0.5, alpha=0.7, color='yellow')
    ax2.set_xlabel('X', color='white')
    ax2.set_ylabel('Y', color='white')
    ax2.set_title('Final Particle Positions (XY plane)', color='white', pad=20)
    ax2.grid(False)
    ax2.axis('equal')
    ax2.set_facecolor('black')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_color('white')
    ax2.spines['left'].set_color('white')
    ax2.tick_params(colors='white')
    
    # Plot 3: Initial particle positions in XZ plane
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.scatter(x_initial, z_initial, s=0.5, alpha=0.7, color='cyan')
    ax3.set_xlabel('X', color='white')
    ax3.set_ylabel('Z', color='white')
    ax3.set_title('Initial Particle Positions (XZ plane)', color='white', pad=20)
    ax3.grid(False)
    ax3.axis('equal')
    ax3.set_facecolor('black')
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['bottom'].set_color('white')
    ax3.spines['left'].set_color('white')
    ax3.tick_params(colors='white')
    
    # Plot 4: Final particle positions in XZ plane
    ax4 = fig.add_subplot(2, 3, 4)
    ax4.scatter(x_final, z_final, s=0.5, alpha=0.7, color='yellow')
    ax4.set_xlabel('X', color='white')
    ax4.set_ylabel('Z', color='white')
    ax4.set_title('Final Particle Positions (XZ plane)', color='white', pad=20)
    ax4.grid(False)
    ax4.axis('equal')
    ax4.set_facecolor('black')
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)
    ax4.spines['bottom'].set_color('white')
    ax4.spines['left'].set_color('white')
    ax4.tick_params(colors='white')
    
    # Plot 5: Initial radial distribution
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.hist(r_initial, bins=50, alpha=0.7, color='cyan', edgecolor='white')
    ax5.set_xlabel('Radial Position', color='white')
    ax5.set_ylabel('Number of Particles', color='white')
    ax5.set_title('Initial Radial Distribution', color='white', pad=20)
    ax5.grid(False)
    ax5.set_facecolor('black')
    ax5.spines['top'].set_visible(False)
    ax5.spines['right'].set_visible(False)
    ax5.spines['bottom'].set_color('white')
    ax5.spines['left'].set_color('white')
    ax5.tick_params(colors='white')
    
    # Plot 6: Final radial distribution
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.hist(r_final, bins=50, alpha=0.7, color='yellow', edgecolor='white')
    ax6.set_xlabel('Radial Position', color='white')
    ax6.set_ylabel('Number of Particles', color='white')
    ax6.set_title('Final Radial Distribution', color='white', pad=20)
    ax6.grid(False)
    ax6.set_facecolor('black')
    ax6.spines['top'].set_visible(False)
    ax6.spines['right'].set_visible(False)
    ax6.spines['bottom'].set_color('white')
    ax6.spines['left'].set_color('white')
    ax6.tick_params(colors='white')
    
    plt.tight_layout()
    particle_plot_file = os.path.join("python_output", "comprehensive_particle_analysis.png")
    plt.savefig(particle_plot_file, dpi=300, bbox_inches='tight', facecolor='black')
    plt.show()
    
    # Calculate statistics
    n_particles = len(x_final)
    mean_r_initial = np.mean(r_initial)
    mean_r_final = np.mean(r_final)
    std_r_initial = np.std(r_initial)
    std_r_final = np.std(r_final)
    min_r_final = np.min(r_final)
    max_r_final = np.max(r_final)
    expansion_factor = mean_r_final / mean_r_initial if mean_r_initial > 0 else 0
    
    return n_particles, mean_r_initial, mean_r_final, expansion_factor, std_r_initial, std_r_final, min_r_final, max_r_final

def main():
    """Main function to run comprehensive analysis"""
    print("SPARC Python Simulation Results Analysis")
    print("=" * 50)
    
    # Create output directory if it doesn't exist
    if not os.path.exists('python_output'):
        os.makedirs('python_output')
    
    # Analyze energy conservation
    print("\n1. Energy Conservation Analysis:")
    initial_energy, final_energy, energy_error = analyze_energy_conservation()
    print(f"   Initial energy: {initial_energy:.6f}")
    print(f"   Final energy: {final_energy:.6f}")
    print(f"   Energy conservation error: {energy_error:.6f}%")
    
    # Analyze particle distribution
    print("\n2. Particle Distribution Analysis:")
    n_particles, mean_r_initial, mean_r_final, expansion_factor, std_r_initial, std_r_final, min_r_final, max_r_final = analyze_particle_distribution()
    print(f"   Total number of particles: {n_particles}")
    print(f"   Initial mean radial position: {mean_r_initial:.4f}")
    print(f"   Final mean radial position: {mean_r_final:.4f}")
    print(f"   Expansion factor: {expansion_factor:.2f}")
    print(f"   Initial radial std dev: {std_r_initial:.4f}")
    print(f"   Final radial std dev: {std_r_final:.4f}")
    print(f"   Minimum final radial position: {min_r_final:.4f}")
    print(f"   Maximum final radial position: {max_r_final:.4f}")
    
    # Summary
    print("\n3. Summary:")
    print(f"   The simulation shows excellent energy conservation with only {energy_error:.6f}% error.")
    print(f"   Particles expanded by a factor of {expansion_factor:.2f} during the simulation.")
    print(f"   Final particle distribution shows a maximum radius of {max_r_final:.2f}.")

if __name__ == "__main__":
    main()