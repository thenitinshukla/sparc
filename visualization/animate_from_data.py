#!/usr/bin/env python3
"""
SPARC Particle Animation from Saved Data
Creates animations from the binary particle position files
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import os
import re
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

def create_animation_from_files(pattern, output_file='sparc_animation.mp4'):
    """Create animation from particle data files"""
    # Get all files matching the pattern
    files = sorted(glob.glob(pattern))
    
    if not files:
        print(f"No files found matching pattern: {pattern}")
        return
    
    print(f"Found {len(files)} files for animation")
    
    # Load first file to get parameters
    step, n_particles, x, y, z = load_particle_data(files[0])
    if step is None or x is None or y is None:
        print("Failed to load first file")
        return
    
    # Create figure with cosmic aesthetics
    fig, ax = plt.subplots(figsize=(10, 10), dpi=100)
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
    
    # Calculate initial distances for coloring
    distances = np.sqrt(x**2 + y**2)
    
    # Create initial scatter plot
    scatter = ax.scatter(x, y, c=distances, cmap=cmap, s=1, alpha=0.8, edgecolors='none')
    
    # Add central glow effect
    central_glow = patches.Circle((0, 0), radius=0.1, color='yellow', alpha=0.3)
    ax.add_patch(central_glow)
    
    # Add title
    title = fig.suptitle('SPARC Particle Simulation', color='white', fontsize=16)
    
    # Animation function
    def animate(frame_idx):
        # Load particle data for this frame
        filename = files[frame_idx]
        step, n_particles, x, y, z = load_particle_data(filename)
        
        if step is None or x is None or y is None:
            return scatter, central_glow, title
        
        # Calculate distances for coloring
        distances = np.sqrt(x**2 + y**2)
        
        # Update scatter plot
        scatter.set_offsets(np.column_stack((x, y)))
        scatter.set_array(distances)
        
        # Update central glow
        central_glow.set_alpha(0.2 + 0.1 * np.sin(frame_idx * 0.1))
        
        # Update title with frame info
        title.set_text(f'SPARC Particle Simulation - Step {step}')
        
        return scatter, central_glow, title
    
    # Create animation
    anim = FuncAnimation(fig, animate, frames=len(files), interval=100, blit=True, repeat=True)
    
    # Show the animation
    plt.tight_layout()
    plt.show()
    
    # Optionally save as MP4
    if output_file:
        print(f"Saving animation as {output_file}...")
        try:
            anim.save(output_file, writer='ffmpeg', fps=10, dpi=100)
            print(f"Animation saved as {output_file}")
        except Exception as e:
            print(f"Error saving animation: {e}")
            print("Make sure ffmpeg is installed for MP4 export")
    
    return anim

def create_still_image_from_file(filename, output_file='sparc_frame.png'):
    """Create a still image from a single particle data file"""
    # Load particle data
    step, n_particles, x, y, z = load_particle_data(filename)
    if step is None or x is None or y is None:
        print("Failed to load file")
        return
    
    # Create figure with cosmic aesthetics (high DPI for stunning visuals)
    fig, ax = plt.subplots(figsize=(12, 12), dpi=500)
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
    ax.scatter(x, y, c=distances, cmap=cmap, s=1.5, alpha=0.8, edgecolors='none')
    
    # Glow layers for artistic effect
    for i in range(1, 4):
        alpha = 0.3 / i
        size = 1.5 + i * 0.5
        ax.scatter(x, y, c=distances, cmap=cmap, s=size, alpha=alpha, edgecolors='none')
    
    # Add central glow effect
    circle1 = patches.Circle((0, 0), 0.05, color='yellow', alpha=0.4)
    circle2 = patches.Circle((0, 0), 0.1, color='cyan', alpha=0.2)
    circle3 = patches.Circle((0, 0), 0.2, color='blue', alpha=0.1)
    ax.add_patch(circle1)
    ax.add_patch(circle2)
    ax.add_patch(circle3)
    
    # Add title
    ax.set_title(f'SPARC Particle Simulation - Step {step}', 
                color='white', fontsize=14, pad=20)
    
    # Save with high DPI for maximum aesthetic impact
    plt.tight_layout()
    plt.savefig(output_file, dpi=500, bbox_inches='tight', 
                facecolor='black', edgecolor='none')
    plt.show()
    
    print(f"Image saved as {output_file}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python animate_from_data.py animate <species> [output.mp4]")
        print("  python animate_from_data.py image <filename> [output.png]")
        print()
        print("Examples:")
        print("  python animate_from_data.py animate electron animation.mp4")
        print("  python animate_from_data.py image output/positions_electron_step_0.bin frame.png")
        return
    
    command = sys.argv[1]
    
    if command == "animate":
        if len(sys.argv) < 3:
            print("Please specify species (electron, ion, or proton)")
            return
        
        species = sys.argv[2]
        pattern = f"output/positions_{species}_step_*.bin"
        output_file = sys.argv[3] if len(sys.argv) > 3 else f"sparc_{species}_animation.mp4"
        
        print(f"Creating animation for {species} particles...")
        create_animation_from_files(pattern, output_file)
        
    elif command == "image":
        if len(sys.argv) < 3:
            print("Please specify filename")
            return
        
        filename = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else "sparc_frame.png"
        
        print(f"Creating image from {filename}...")
        create_still_image_from_file(filename, output_file)
        
    else:
        print(f"Unknown command: {command}")
        print("Use 'animate' or 'image'")

if __name__ == "__main__":
    main()