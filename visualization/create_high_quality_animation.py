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

def create_frame_image(time_step, output_dir="output"):
    """Create a single frame image for a specific time step"""
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
    
    # Create figure with cosmic aesthetics (high DPI for stunning visuals)
    fig, ax = plt.subplots(figsize=(12, 12), dpi=150)
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Remove axes for minimalist design
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    
    # Plot each species with different colors and sizes
    if len(ex) > 0:
        ax.scatter(ex, ey, s=0.3, c='cyan', alpha=0.7, label='Electrons', rasterized=True)
    
    if len(ix) > 0:
        ax.scatter(ix, iy, s=0.6, c='magenta', alpha=0.7, label='Ions', rasterized=True)
    
    if len(px) > 0:
        ax.scatter(px, py, s=0.4, c='yellow', alpha=0.7, label='Protons', rasterized=True)
    
    # Add legend
    legend = ax.legend(loc='upper right', facecolor='black', edgecolor='white', fontsize=12)
    for text in legend.get_texts():
        text.set_color('white')
    
    # Add title
    ax.set_title(f'SPARC: Simulation of Particles in A Radial Configuration\nTime Step {time_step}', 
                color='white', fontsize=16, pad=20)
    
    # Save the frame
    frame_filename = f"animation_frames/high_quality_frame_{time_step:04d}.png"
    plt.tight_layout()
    plt.savefig(frame_filename, dpi=150, bbox_inches='tight', facecolor='black')
    plt.close(fig)
    
    return frame_filename

def create_high_quality_animation():
    """Create a high-quality animation with all particle species"""
    # Get all time steps
    output_dir = "output"
    electron_files = sorted(glob.glob(os.path.join(output_dir, "positions_electron_step_*.bin")))
    
    # Extract time steps
    time_steps = sorted(list(set([int(f.split('_')[-1].split('.')[0]) for f in electron_files])))
    
    if not time_steps:
        print("No particle data files found!")
        return
    
    print(f"Found {len(time_steps)} time steps")
    
    # Create animation frames directory if it doesn't exist
    if not os.path.exists("animation_frames"):
        os.makedirs("animation_frames")
    
    # Create frames
    frame_files = []
    for i, time_step in enumerate(time_steps[::5]):  # Use every 5th frame to reduce file size
        print(f"Creating frame {i+1}/{len(time_steps[::5])} (time step {time_step})")
        try:
            frame_file = create_frame_image(time_step, output_dir)
            frame_files.append(frame_file)
        except Exception as e:
            print(f"Error creating frame for time step {time_step}: {e}")
    
    if frame_files:
        # Create animated GIF from frames
        print("Creating animated GIF from frames...")
        frames = []
        for frame_file in frame_files:
            try:
                # Load and resize frame for consistent size
                img = Image.open(frame_file)
                frames.append(img)
            except Exception as e:
                print(f"Error loading frame {frame_file}: {e}")
        
        if frames:
            print("Saving high_quality_sparc_animation.gif...")
            # Save as animated GIF
            frames[0].save(
                'high_quality_sparc_animation.gif',
                save_all=True,
                append_images=frames[1:],
                duration=200,  # 200ms per frame = 5 FPS
                loop=0
            )
            print("High-quality animation saved successfully!")
            
            # Close all frames
            for frame in frames:
                frame.close()
        else:
            print("No frames were loaded successfully!")
    else:
        print("No frames were created successfully!")

if __name__ == "__main__":
    create_high_quality_animation()