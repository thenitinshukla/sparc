import numpy as np
import matplotlib.pyplot as plt
import struct
import os

def load_particle_data(filename):
    """Load particle positions from binary file"""
    try:
        with open(filename, 'rb') as f:
            # Read step number (int)
            step_data = f.read(4)
            if len(step_data) < 4:
                return np.array([]), np.array([]), np.array([])
            step = struct.unpack('i', step_data)[0]
            
            # Read number of particles (int)
            n_particles_data = f.read(4)
            if len(n_particles_data) < 4:
                return np.array([]), np.array([]), np.array([])
            n_particles = struct.unpack('i', n_particles_data)[0]
            
            if n_particles <= 0:
                return np.array([]), np.array([]), np.array([])
            
            # Read particle positions (3 arrays of doubles)
            x_data = f.read(n_particles * 8)
            y_data = f.read(n_particles * 8)
            z_data = f.read(n_particles * 8)
            
            if len(x_data) < n_particles * 8 or len(y_data) < n_particles * 8 or len(z_data) < n_particles * 8:
                return np.array([]), np.array([]), np.array([])
            
            x = np.array(struct.unpack(f'{n_particles}d', x_data))
            y = np.array(struct.unpack(f'{n_particles}d', y_data))
            z = np.array(struct.unpack(f'{n_particles}d', z_data))
            
            return x, y, z
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return np.array([]), np.array([]), np.array([])

def create_combined_visualization():
    """Create a high-quality static visualization with all particle species"""
    # Use a middle time step for the visualization
    time_step = 5000  # You can change this to any available time step
    
    # Load data for each species
    electron_file = f"output/positions_electron_step_{time_step}.bin"
    ion_file = f"output/positions_ion_step_{time_step}.bin"
    proton_file = f"output/positions_proton_step_{time_step}.bin"
    
    print(f"Creating visualization for time step {time_step}")
    
    # Load electron data
    ex, ey, ez = load_particle_data(electron_file) if os.path.exists(electron_file) else (np.array([]), np.array([]), np.array([]))
    print(f"Loaded {len(ex)} electrons")
    
    # Load ion data
    ix, iy, iz = load_particle_data(ion_file) if os.path.exists(ion_file) else (np.array([]), np.array([]), np.array([]))
    print(f"Loaded {len(ix)} ions")
    
    # Load proton data
    px, py, pz = load_particle_data(proton_file) if os.path.exists(proton_file) else (np.array([]), np.array([]), np.array([]))
    print(f"Loaded {len(px)} protons")
    
    # Create figure with cosmic aesthetics (high DPI for stunning visuals)
    fig, ax = plt.subplots(figsize=(12, 12), dpi=300)
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Remove axes for minimalist design
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    
    # Plot each species with different colors and sizes
    if len(ex) > 0:
        ax.scatter(ex, ey, s=0.1, c='cyan', alpha=0.7, label='Electrons', rasterized=True)
    
    if len(ix) > 0:
        ax.scatter(ix, iy, s=0.3, c='magenta', alpha=0.7, label='Ions', rasterized=True)
    
    if len(px) > 0:
        ax.scatter(px, py, s=0.2, c='yellow', alpha=0.7, label='Protons', rasterized=True)
    
    # Add legend
    legend = ax.legend(loc='upper right', facecolor='black', edgecolor='white', fontsize=12)
    for text in legend.get_texts():
        text.set_color('white')
    
    # Add title
    ax.set_title(f'SPARC: Simulation of Particles in A Radial Configuration\nTime Step {time_step}', 
                color='white', fontsize=16, pad=20)
    
    # Save the visualization
    output_file = 'combined_sparc_visualization.png'
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='black')
    print(f"Visualization saved as {output_file}")
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    create_combined_visualization()