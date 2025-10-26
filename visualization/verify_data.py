import numpy as np
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
                return None, None, None, None
            step = struct.unpack('i', step_data)[0]
            
            # Read number of particles (int)
            n_particles_data = f.read(4)
            if len(n_particles_data) < 4:
                return step, None, None, None
            n_particles = struct.unpack('i', n_particles_data)[0]
            
            print(f"File: {filename}")
            print(f"  Time step: {step}")
            print(f"  Number of particles: {n_particles}")
            
            if n_particles <= 0:
                return step, n_particles, np.array([]), np.array([])
            
            # Read particle positions (3 arrays of doubles)
            x_data = f.read(n_particles * 8)
            y_data = f.read(n_particles * 8)
            z_data = f.read(n_particles * 8)
            
            if len(x_data) < n_particles * 8 or len(y_data) < n_particles * 8 or len(z_data) < n_particles * 8:
                return step, n_particles, None, None
            
            x = np.array(struct.unpack(f'{n_particles}d', x_data))
            y = np.array(struct.unpack(f'{n_particles}d', y_data))
            z = np.array(struct.unpack(f'{n_particles}d', z_data))
            
            print(f"  X range: {np.min(x):.3f} to {np.max(x):.3f}")
            print(f"  Y range: {np.min(y):.3f} to {np.max(y):.3f}")
            print(f"  Z range: {np.min(z):.3f} to {np.max(z):.3f}")
            
            return step, n_particles, x, y
            
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None, None, None, None

def verify_data():
    """Verify that the simulation data is correct"""
    output_dir = "output"
    
    # Check a few files for each species
    species_list = ["electron", "ion", "proton"]
    
    for species in species_list:
        files = sorted(glob.glob(os.path.join(output_dir, f"positions_{species}_step_*.bin")))
        print(f"\n=== {species.capitalize()} Files ({len(files)} found) ===")
        
        if files:
            # Check first, middle, and last files
            indices = [0, len(files)//2, -1] if len(files) > 2 else [0, min(1, len(files)-1)]
            for i in indices:
                if i < len(files):
                    file = files[i]
                    step, n_particles, x, y = load_particle_data(file)
                    if step is not None and n_particles is not None:
                        print(f"  File {i+1}/{len(files)}: {os.path.basename(file)} - OK")
                    else:
                        print(f"  File {i+1}/{len(files)}: {os.path.basename(file)} - ERROR")

if __name__ == "__main__":
    verify_data()