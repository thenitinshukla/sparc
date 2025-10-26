#!/usr/bin/env python3
"""
SPARC Particle Frame Generator
Creates a sequence of high-quality frames from saved particle data
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import os
import glob

def load_particle_data(filename):
    """Load particle positions from binary file"""
    try:
        with open(filename, 'rb') as f:
            # Read step number
            step = np.frombuffer(f.read(4), dtype=np.int32)[0]
            
            # Read number of particles
            n_particles = np.frombuffer(f.read(4), dtype=np.int32)[0]
            
            # Read particle positions
            x = np.frombuffer(f.read(n_particles * 8), dtype=np.float64)
            y = np.frombuffer(f.read(n_particles * 8), dtype=np.float64)
            z = np.frombuffer(f.read(n_particles * 8), dtype=np.float64)
            
        return step, n_particles, x, y, z
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None, None, None, None, None

def create_cosmic_cmap():
    """Create a cosmic color gradient colormap"""
    colors = ['black', 'purple', 'blue', 'cyan', 'white']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('cosmic', colors, N=n_bins)
    return cmap

def create_frame_from_data(filename, output_dir='animation_frames'):
    """Create a high-quality frame from particle data"""
    # Load particle data
    step, n_particles, x, y, z = load_particle_data(filename)
    if step is None or x is None or y is None:
        print(f"Failed to load {filename}")
        return False
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create figure with cosmic aesthetics (high DPI for stunning visuals)
    fig, ax = plt.subplots(figsize=(12, 12), dpi=300)  # Reduced DPI for faster processing
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Remove axes for minimalist design
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Set limits
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    
    # Create cosmic colormap
    cmap = create_cosmic_cmap()
    
    # Calculate distances for coloring
    distances = np.sqrt(x**2 + y**2)
    
    # Create scatter plot with multiple glow layers
    # Base layer
    ax.scatter(x, y, c=distances, cmap=cmap, s=1.0, alpha=0.8, edgecolors='none')
    
    # Glow layers for artistic effect
    for i in range(1, 3):
        alpha = 0.3 / i
        size = 1.0 + i * 0.3
        ax.scatter(x, y, c=distances, cmap=cmap, s=size, alpha=alpha, edgecolors='none')
    
    # Add central glow effect
    circle1 = patches.Circle((0, 0), 0.05, color='yellow', alpha=0.4)
    circle2 = patches.Circle((0, 0), 0.1, color='cyan', alpha=0.2)
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    
    # Add title
    ax.set_title(f'SPARC Particle Simulation - Step {step}', 
                color='white', fontsize=12, pad=20)
    
    # Save frame
    output_filename = os.path.join(output_dir, f"frame_{step:04d}.png")
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight', 
                facecolor='black', edgecolor='none')
    plt.close(fig)
    
    print(f"Saved frame {step} as {output_filename}")
    return True

def generate_all_frames(pattern, output_dir='animation_frames'):
    """Generate frames for all particle data files matching the pattern"""
    # Get all files matching the pattern
    files = sorted(glob.glob(pattern))
    
    if not files:
        print(f"No files found matching pattern: {pattern}")
        return
    
    print(f"Found {len(files)} files for frame generation")
    
    # Process each file
    success_count = 0
    for filename in files:
        if create_frame_from_data(filename, output_dir):
            success_count += 1
    
    print(f"Successfully generated {success_count} frames out of {len(files)} files")
    print(f"Frames saved in '{output_dir}' directory")
    
    # Instructions for creating animation
    print("\nTo create an animation from these frames, you can use ffmpeg:")
    print("ffmpeg -r 10 -i animation_frames/frame_%04d.png -c:v libx264 -pix_fmt yuv420p sparc_animation.mp4")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python generate_frames.py <species>")
        print()
        print("Examples:")
        print("  python generate_frames.py electron")
        print("  python generate_frames.py ion")
        print("  python generate_frames.py proton")
        return
    
    species = sys.argv[1]
    pattern = f"output/positions_{species}_step_*.bin"
    
    print(f"Generating frames for {species} particles...")
    generate_all_frames(pattern)

if __name__ == "__main__":
    main()