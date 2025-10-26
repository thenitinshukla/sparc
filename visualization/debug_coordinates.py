import numpy as np
import struct
import os

def load_particle_data(filename):
    """Load particle positions from binary file"""
    try:
        with open(filename, 'rb') as f:
            # Read step number (int)
            step_data = f.read(4)
            if len(step_data) < 4:
                return None, None, None, None, None, None
            step = struct.unpack('i', step_data)[0]
            
            # Read number of particles (int)
            n_particles_data = f.read(4)
            if len(n_particles_data) < 4:
                return step, None, None, None, None, None
            n_particles = struct.unpack('i', n_particles_data)[0]
            
            if n_particles <= 0:
                return step, n_particles, np.array([]), np.array([]), np.array([]), np.array([])
            
            # Read particle positions (3 arrays of doubles)
            x_data = f.read(n_particles * 8)
            y_data = f.read(n_particles * 8)
            z_data = f.read(n_particles * 8)
            
            if len(x_data) < n_particles * 8 or len(y_data) < n_particles * 8 or len(z_data) < n_particles * 8:
                return step, n_particles, None, None, None, None
            
            x = np.array(struct.unpack(f'{n_particles}d', x_data))
            y = np.array(struct.unpack(f'{n_particles}d', y_data))
            z = np.array(struct.unpack(f'{n_particles}d', z_data))
            
            r = np.sqrt(x*x + y*y + z*z)
            
            return step, n_particles, x, y, z, r
            
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None, None, None, None, None, None

def debug_coordinates():
    """Debug the coordinate ranges in the particle data"""
    output_dir = "output"
    
    # Check a few files for each species at time step 0
    species_list = ["electron", "ion", "proton"]
    
    for species in species_list:
        file = os.path.join(output_dir, f"positions_{species}_step_0.bin")
        if os.path.exists(file):
            print(f"\n=== {species.capitalize()} Data at Time Step 0 ===")
            step, n_particles, x, y, z, r = load_particle_data(file)
            if step is not None and n_particles is not None:
                if x is not None and len(x) > 0:
                    print(f"Time step: {step}")
                    print(f"Number of particles: {n_particles}")
                    print(f"X range: {np.min(x):.6f} to {np.max(x):.6f}")
                    print(f"Y range: {np.min(y):.6f} to {np.max(y):.6f}")
                    print(f"Z range: {np.min(z):.6f} to {np.max(z):.6f}")
                    print(f"R range: {np.min(r):.6f} to {np.max(r):.6f}")
                    print(f"Mean R: {np.mean(r):.6f}")
                    print(f"Median R: {np.median(r):.6f}")
                    
                    # Check how many particles are within different ranges
                    ranges = [0.1, 0.5, 1.0, 1.5, 2.0, 5.0, 10.0]
                    for r_max in ranges:
                        count = np.sum(r <= r_max)
                        print(f"Particles within radius {r_max}: {count}/{n_particles} ({100*count/n_particles:.1f}%)")
                else:
                    print(f"No particle data in file {file}")
            else:
                print(f"Error reading file {file}")

if __name__ == "__main__":
    debug_coordinates()