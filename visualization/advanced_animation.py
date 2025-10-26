import numpy as np
import matplotlib.pyplot as plt
import struct
import os
import glob
from PIL import Image

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

def create_frame(time_step, output_dir="output"):
    """Create a single frame for a specific time step and return image data"""
    # Load data for each species
    electron_file = os.path.join(output_dir, f"positions_electron_step_{time_step}.bin")
    ion_file = os.path.join(output_dir, f"positions_ion_step_{time_step}.bin")
    proton_file = os.path.join(output_dir, f"positions_proton_step_{time_step}.bin")
    
    # Load electron data
    ex, ey, ez = load_particle_data(electron_file) if os.path.exists(electron_file) else (np.array([]), np.array([]), np.array([]))
    
    # Load ion data
    ix, iy, iz = load_particle_data(ion_file) if os.path.exists(ion_file) else (np.array([]), np.array([]), np.array([]))
    
    # Load proton data
    px, py, pz = load_particle_data(proton_file) if os.path.exists(proton_file) else (np.array([]), np.array([]), np.array([]))
    
    # Create figure with cosmic aesthetics
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Remove axes for minimalist design
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    
    # Plot each species with different colors and sizes
    if len(ex) > 0:
        ax.scatter(ex, ey, s=0.5, c='cyan', alpha=0.6, label='Electrons', rasterized=True)
    
    if len(ix) > 0:
        ax.scatter(ix, iy, s=1.0, c='magenta', alpha=0.6, label='Ions', rasterized=True)
    
    if len(px) > 0:
        ax.scatter(px, py, s=0.8, c='yellow', alpha=0.6, label='Protons', rasterized=True)
    
    # Add legend
    legend = ax.legend(loc='upper right', facecolor='black', edgecolor='white', fontsize=10)
    for text in legend.get_texts():
        text.set_color('white')
    
    # Add title
    ax.set_title(f'SPARC Simulation - Time Step {time_step}', 
                color='white', fontsize=14, pad=15)
    
    # Save to a temporary file
    temp_filename = f'temp_frame_{time_step}.png'
    plt.tight_layout()
    plt.savefig(temp_filename, dpi=100, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    
    # Load the image and remove the temporary file
    img = Image.open(temp_filename)
    img.load()  # Load the image data
    os.remove(temp_filename)  # Remove temporary file
    
    return img

def create_advanced_animation():
    """Create an advanced animation with all particle species"""
    # Get all time steps
    output_dir = "output"
    electron_files = sorted(glob.glob(os.path.join(output_dir, "positions_electron_step_*.bin")))
    
    # Extract time steps
    time_steps = sorted(list(set([int(f.split('_')[-1].split('.')[0]) for f in electron_files])))
    
    if not time_steps:
        print("No particle data files found!")
        return
    
    print(f"Found {len(time_steps)} time steps")
    
    # Create frames
    frames = []
    for i, time_step in enumerate(time_steps):
        print(f"Processing frame {i+1}/{len(time_steps)} (time step {time_step})")
        try:
            img = create_frame(time_step, output_dir)
            frames.append(img)
        except Exception as e:
            print(f"Error creating frame for time step {time_step}: {e}")
    
    if frames:
        # Save as animated GIF
        print("Saving animation as advanced_sparc_animation.gif...")
        frames[0].save(
            'advanced_sparc_animation.gif',
            save_all=True,
            append_images=frames[1:],
            duration=100,  # 100ms per frame = 10 FPS
            loop=0
        )
        print("Animation saved successfully!")
        
        # Close all images to free memory
        for frame in frames:
            frame.close()
    else:
        print("No frames were created successfully!")

if __name__ == "__main__":
    create_advanced_animation()