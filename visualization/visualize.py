#!/usr/bin/env python3
"""
SPARC Particle Visualization using pyOpenGL
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import sys
import os
import struct

def read_particle_data(filename):
    """Read particle positions from binary file"""
    try:
        with open(filename, 'rb') as f:
            # Read time step (int)
            step = struct.unpack('i', f.read(4))[0]
            
            # Read number of particles (int)
            n_particles = struct.unpack('i', f.read(4))[0]
            
            # Read particle positions
            x = np.array(struct.unpack(f'{n_particles}d', f.read(8 * n_particles)))
            y = np.array(struct.unpack(f'{n_particles}d', f.read(8 * n_particles)))
            z = np.array(struct.unpack(f'{n_particles}d', f.read(8 * n_particles)))
            
        return step, x, y, z
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return None, None, None, None

def visualize_static(x, y, z, title="SPARC Particle Visualization"):
    """Create a static 3D visualization of particles"""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create scatter plot
    ax.scatter(x, y, z, c='blue', s=1, alpha=0.7)
    
    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)
    
    # Set equal aspect ratio
    max_range = np.array([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]).max() / 2.0
    mid_x = (x.max()+x.min()) * 0.5
    mid_y = (y.max()+y.min()) * 0.5
    mid_z = (z.max()+z.min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    plt.tight_layout()
    plt.show()

def create_animation(particle_files, output_file="sparc_animation.gif"):
    """Create an animation from multiple particle data files"""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Collect all particle data
    frames = []
    steps = []
    
    for filename in particle_files:
        step, x, y, z = read_particle_data(filename)
        if step is not None:
            frames.append((x, y, z))
            steps.append(step)
    
    if not frames:
        print("No valid data found")
        return
    
    # Determine global bounds
    all_x = np.concatenate([frame[0] for frame in frames])
    all_y = np.concatenate([frame[1] for frame in frames])
    all_z = np.concatenate([frame[2] for frame in frames])
    
    max_range = np.array([all_x.max()-all_x.min(), all_y.max()-all_y.min(), all_z.max()-all_z.min()]).max() / 2.0
    mid_x = (all_x.max()+all_x.min()) * 0.5
    mid_y = (all_y.max()+all_y.min()) * 0.5
    mid_z = (all_z.max()+all_z.min()) * 0.5
    
    def update(frame_idx):
        ax.clear()
        x, y, z = frames[frame_idx]
        
        ax.scatter(x, y, z, c='blue', s=1, alpha=0.7)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title(f'SPARC Particle Visualization - Step {steps[frame_idx]}')
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        
        return ax
    
    # Create animation
    anim = animation.FuncAnimation(fig, update, frames=len(frames), interval=200, blit=False)
    
    # Save animation
    anim.save(output_file, writer='pillow', fps=5)
    print(f"Animation saved as {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <particle_data_file> [output.gif]")
        print("   or: python visualize.py --animate <file1> <file2> ... [output.gif]")
        return
    
    if sys.argv[1] == "--animate":
        # Animation mode
        particle_files = []
        output_file = "sparc_animation.gif"
        
        for arg in sys.argv[2:]:
            if arg.endswith('.gif'):
                output_file = arg
            else:
                particle_files.append(arg)
        
        if not particle_files:
            print("No particle data files provided")
            return
            
        create_animation(particle_files, output_file)
    else:
        # Static visualization mode
        filename = sys.argv[1]
        step, x, y, z = read_particle_data(filename)
        
        if step is None:
            print("Failed to read particle data")
            return
            
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        visualize_static(x, y, z, f"SPARC Particle Visualization - Step {step}")

if __name__ == "__main__":
    main()