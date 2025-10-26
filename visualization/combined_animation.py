import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
import os
import glob

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

def create_combined_animation():
    """Create animation with all particle species"""
    # Get all time steps
    output_dir = "output"
    electron_files = sorted(glob.glob(os.path.join(output_dir, "positions_electron_step_*.bin")))
    ion_files = sorted(glob.glob(os.path.join(output_dir, "positions_ion_step_*.bin")))
    proton_files = sorted(glob.glob(os.path.join(output_dir, "positions_proton_step_*.bin")))
    
    # Extract time steps
    time_steps = sorted(list(set([int(f.split('_')[-1].split('.')[0]) for f in electron_files])))
    
    if not time_steps:
        print("No particle data files found!")
        return
    
    print(f"Found {len(time_steps)} time steps")
    
    # Create figure with cosmic aesthetics
    fig, ax = plt.subplots(figsize=(12, 12), dpi=200)
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Remove axes for minimalist design
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    
    # Create title
    title = fig.suptitle('SPARC: Simulation of Particles in A Radial Configuration', 
                         color='white', fontsize=16, y=0.95)
    
    # Initialize scatter plots for each species with cosmic colors
    electron_scatter = ax.scatter([], [], s=0.1, c='cyan', alpha=0.7, label='Electrons')
    ion_scatter = ax.scatter([], [], s=0.3, c='magenta', alpha=0.7, label='Ions')
    proton_scatter = ax.scatter([], [], s=0.2, c='yellow', alpha=0.7, label='Protons')
    
    # Add legend
    legend = ax.legend(loc='upper right', facecolor='black', edgecolor='white')
    for text in legend.get_texts():
        text.set_color('white')
    
    def animate(frame_idx):
        time_step = time_steps[frame_idx]
        print(f"Processing frame {frame_idx+1}/{len(time_steps)} (time step {time_step})")
        
        # Load data for each species
        electron_file = f"output/positions_electron_step_{time_step}.bin"
        ion_file = f"output/positions_ion_step_{time_step}.bin"
        proton_file = f"output/positions_proton_step_{time_step}.bin"
        
        # Load electron data
        if os.path.exists(electron_file):
            ex, ey, ez = load_particle_data(electron_file)
            electron_scatter.set_offsets(np.column_stack((ex, ey)) if len(ex) > 0 else np.empty((0, 2)))
        else:
            electron_scatter.set_offsets(np.empty((0, 2)))
            
        # Load ion data
        if os.path.exists(ion_file):
            ix, iy, iz = load_particle_data(ion_file)
            ion_scatter.set_offsets(np.column_stack((ix, iy)) if len(ix) > 0 else np.empty((0, 2)))
        else:
            ion_scatter.set_offsets(np.empty((0, 2)))
            
        # Load proton data
        if os.path.exists(proton_file):
            px, py, pz = load_particle_data(proton_file)
            proton_scatter.set_offsets(np.column_stack((px, py)) if len(px) > 0 else np.empty((0, 2)))
        else:
            proton_scatter.set_offsets(np.empty((0, 2)))
            
        # Update title with time step
        title.set_text(f'SPARC: Simulation of Particles in A Radial Configuration - Time Step {time_step}')
        
        return electron_scatter, ion_scatter, proton_scatter, title
    
    # Create animation
    print("Creating animation...")
    anim = animation.FuncAnimation(fig, animate, frames=len(time_steps), 
                                  interval=50, blit=True, repeat=True)
    
    # Save animation
    print("Saving animation as combined_sparc_animation.gif...")
    anim.save('combined_sparc_animation.gif', writer='pillow', fps=10)
    print("Animation saved successfully!")
    
    # Show the plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    create_combined_animation()