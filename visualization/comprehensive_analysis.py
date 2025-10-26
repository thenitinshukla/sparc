import numpy as np
import matplotlib.pyplot as plt
import os
import struct
import glob

# Set up the plot style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 10)
plt.rcParams['font.size'] = 12

def read_binary_file(filename):
    """Read particle positions from binary file"""
    with open(filename, 'rb') as f:
        # Read time step (int) and number of particles (int)
        step = struct.unpack('i', f.read(4))[0]
        n_particles = struct.unpack('i', f.read(4))[0]
        
        # Read particle positions
        x = np.array(struct.unpack(f'{n_particles}d', f.read(8 * n_particles)))
        y = np.array(struct.unpack(f'{n_particles}d', f.read(8 * n_particles)))
        z = np.array(struct.unpack(f'{n_particles}d', f.read(8 * n_particles)))
        
    return step, n_particles, x, y, z

def read_simulation_data(filename):
    """Read simulation data from text file"""
    # Fix the path to look in the correct directory
    if not os.path.exists(filename):
        # Try alternative path
        alt_path = os.path.join('cpp_sparc', filename)
        if os.path.exists(alt_path):
            filename = alt_path
        else:
            # Try another alternative
            alt_path = os.path.join('..', filename)
            if os.path.exists(alt_path):
                filename = alt_path
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Could not find simulation data file: {filename}")
        
    data = np.genfromtxt(filename, delimiter=',', skip_header=1)
    if len(data.shape) == 1:
        data = data.reshape(1, -1)
    return data

def calculate_radial_positions(x, y, z):
    """Calculate radial positions for all particles"""
    return np.sqrt(x**2 + y**2 + z**2)

def plot_total_energy_vs_time(ax, electron_data, proton_data=None):
    """Plot total energy vs time"""
    time_e = electron_data[:, 0]
    energy_e = electron_data[:, 1]
    
    ax.plot(time_e, energy_e, 'cyan', linewidth=2, label='Electrons')
    
    if proton_data is not None:
        time_p = proton_data[:, 0]
        energy_p = proton_data[:, 1]
        ax.plot(time_p, energy_p, 'yellow', linewidth=2, label='Protons')
        # Total energy
        if len(time_e) == len(time_p):
            total_energy = energy_e + energy_p
            ax.plot(time_e, total_energy, 'magenta', linewidth=2, label='Total')
    
    ax.set_xlabel('Time (s)', color='white')
    ax.set_ylabel('Energy', color='white')
    ax.set_title('Total Energy vs Time', color='white', pad=20)
    ax.legend(facecolor='black', edgecolor='white')
    ax.grid(False)
    
    # Style the legend text
    legend = ax.legend()
    for text in legend.get_texts():
        text.set_color('white')
    
    # Style the axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    
    # Style tick labels
    ax.tick_params(colors='white')
    
    # Set background color
    ax.set_facecolor('black')

def plot_particle_positions(ax, x, y, title):
    """Plot particle positions (x,y) with cosmic styling"""
    ax.scatter(x, y, s=1, alpha=0.7, color='cyan', edgecolors='none')
    ax.set_xlabel('X Position', color='white')
    ax.set_ylabel('Y Position', color='white')
    ax.set_title(title, color='white', pad=20)
    ax.grid(False)
    ax.axis('equal')
    
    # Style the axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    
    # Style tick labels
    ax.tick_params(colors='white')
    
    # Set background color
    ax.set_facecolor('black')

def plot_number_of_particles_vs_radial_position(ax, radial_positions, title, color='cyan'):
    """Plot number of particles vs radial positions with improved styling"""
    # Create histogram with more bins for smoother curve
    counts, bins = np.histogram(radial_positions, bins=100)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    # Create a smooth line plot instead of histogram
    ax.plot(bin_centers, counts, color=color, linewidth=2.5, alpha=0.8)
    
    # Fill under the curve with transparency for better visual effect
    ax.fill_between(bin_centers, counts, alpha=0.3, color=color)
    
    # Remove grid for cleaner look
    ax.grid(False)
    
    # Improve labels
    ax.set_xlabel('Radial Position', fontsize=12, color='white')
    ax.set_ylabel('Number of Particles', fontsize=12, color='white')
    ax.set_title(title, fontsize=14, color='white', pad=20)
    
    # Style the axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    
    # Style tick labels
    ax.tick_params(colors='white')
    
    # Set background color
    ax.set_facecolor('black')

def create_comprehensive_visualization():
    """Create comprehensive visualization of simulation data"""
    
    # Set dark background for cosmic aesthetic
    plt.style.use('dark_background')
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor('black')
    
    # Ensure output directory exists
    output_dir = 'cpp_sparc/output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read simulation data with correct paths
    electron_file = 'cpp_sparc/output/simulation_output_electron.txt'
    proton_file = 'cpp_sparc/output/simulation_output_proton.txt'
    
    if not os.path.exists(electron_file):
        raise FileNotFoundError(f"Could not find electron data file: {electron_file}")
        
    electron_data = read_simulation_data(electron_file)
    proton_data = read_simulation_data(proton_file) if os.path.exists(proton_file) else None
    
    # Plot 1: Total Energy vs Time
    ax1 = plt.subplot(2, 2, 1)
    plot_total_energy_vs_time(ax1, electron_data, proton_data)
    
    # Find latest binary files for electron and proton
    electron_files = glob.glob('output/positions_electron_step_*.bin')
    proton_files = glob.glob('output/positions_proton_step_*.bin')
    
    if electron_files:
        # Get the file with the highest step number
        latest_electron_file = max(electron_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        step_e, n_e, x_e, y_e, z_e = read_binary_file(latest_electron_file)
        radial_e = calculate_radial_positions(x_e, y_e, z_e)
        
        # Plot 2: Particle positions (x,y) for electrons
        ax2 = plt.subplot(2, 2, 2)
        plot_particle_positions(ax2, x_e, y_e, f'Electron Positions (Step {step_e})')
        
        # Plot 3: Number of particles vs radial position for electrons (improved)
        ax3 = plt.subplot(2, 2, 3)
        plot_number_of_particles_vs_radial_position(ax3, radial_e, 
                                                   f'Electron Distribution (Step {step_e})',
                                                   color='cyan')
    
    if proton_files:
        # Get the file with the highest step number
        latest_proton_file = max(proton_files, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        step_p, n_p, x_p, y_p, z_p = read_binary_file(latest_proton_file)
        radial_p = calculate_radial_positions(x_p, y_p, z_p)
        
        # Plot 4: Number of particles vs radial position for protons (improved)
        ax4 = plt.subplot(2, 2, 4)
        plot_number_of_particles_vs_radial_position(ax4, radial_p, 
                                                   f'Proton Distribution (Step {step_p})',
                                                   color='yellow')
    
    plt.tight_layout()
    plt.suptitle('SPARC Simulation Analysis', fontsize=16, y=0.98, color='white')
    plt.subplots_adjust(top=0.95)
    
    # Save the plot with high DPI for better quality
    output_path = os.path.join(output_dir, 'comprehensive_analysis_improved.png')
    plt.savefig(output_path, dpi=500, bbox_inches='tight', 
                facecolor='black', edgecolor='none')
    plt.show()

def create_radial_distribution_comparison():
    """Create a comparison plot of radial distributions for different time steps"""
    
    # Find all electron binary files with correct path
    electron_files = glob.glob('cpp_sparc/output/positions_electron_step_*.bin')
    
    if not electron_files:
        print("No electron position files found")
        return
    
    # Sort files by step number
    electron_files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    # Select a few time steps to plot
    selected_files = electron_files[::max(1, len(electron_files)//5)]  # Select ~5 time steps
    
    # Set up dark background for cosmic aesthetic
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12, 8))
    fig.patch.set_facecolor('black')
    ax = fig.add_subplot(111)
    ax.set_facecolor('black')
    
    # Define cosmic color gradient
    colors = ['cyan', 'deepskyblue', 'lightblue', 'white', 'lavender']
    
    for i, filename in enumerate(selected_files):
        step, n_particles, x, y, z = read_binary_file(filename)
        radial = calculate_radial_positions(x, y, z)
        
        # Create smooth distribution
        counts, bins = np.histogram(radial, bins=100, density=True)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        # Plot with cosmic colors
        color = colors[i % len(colors)]
        ax.plot(bin_centers, counts, linewidth=2.5, label=f'Step {step}', color=color, alpha=0.8)
    
    # Style improvements
    ax.set_xlabel('Radial Position', fontsize=14, color='white')
    ax.set_ylabel('Particle Density', fontsize=14, color='white')
    ax.set_title('Radial Distribution Evolution Over Time', fontsize=16, color='white', pad=20)
    
    # Remove grid for cleaner look
    ax.grid(False)
    
    # Style the legend
    legend = ax.legend(facecolor='black', edgecolor='white')
    for text in legend.get_texts():
        text.set_color('white')
    
    # Style the axes
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    
    # Style tick labels
    ax.tick_params(colors='white')
    
    # Ensure output directory exists
    output_dir = 'cpp_sparc/output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'radial_distribution_evolution_improved.png')
    plt.savefig(output_path, dpi=500, bbox_inches='tight',
                facecolor='black', edgecolor='none')
    plt.show()

if __name__ == "__main__":
    print("Creating comprehensive visualization...")
    create_comprehensive_visualization()
    
    print("Creating radial distribution comparison...")
    create_radial_distribution_comparison()
    
    print("Visualizations saved to output directory.")