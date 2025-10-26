#!/usr/bin/env python3
"""
SPARC Particle Visualization using pyOpenGL
Creates visually stunning, artistic N-body visualizations with cosmic color gradients
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import sys
import os

def read_simulation_data(filename):
    """Read simulation data from text file"""
    try:
        # Read header and data
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        # Skip header line
        data_lines = lines[1:]
        
        # Parse data
        time = []
        energy = []
        max_r2 = []
        
        for line in data_lines:
            if line.strip():
                values = line.strip().split(',')
                time.append(float(values[0]))
                energy.append(float(values[1]))
                max_r2.append(float(values[2]))
        
        return np.array(time), np.array(energy), np.array(max_r2)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None, None, None

def create_cosmic_cmap():
    """Create a cosmic color gradient colormap"""
    colors = ['black', 'purple', 'blue', 'cyan', 'white']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('cosmic', colors, N=n_bins)
    return cmap

def visualize_static_particles(x, y, z, title="SPARC Particle Visualization", dpi=500):
    """Create a static 3D visualization of particles with cosmic aesthetics"""
    fig = plt.figure(figsize=(12, 10), dpi=dpi)
    ax = fig.add_subplot(111, projection='3d')
    
    # Create cosmic colormap
    cmap = create_cosmic_cmap()
    
    # Calculate distance from origin for coloring
    distances = np.sqrt(x**2 + y**2 + z**2)
    
    # Create scatter plot with cosmic colors
    scatter = ax.scatter(x, y, z, c=distances, cmap=cmap, s=1, alpha=0.7)
    
    # Add multiple glow layers for artistic effect
    for i in range(3):
        alpha = 0.3 / (i + 1)
        size = 1 + i * 0.5
        ax.scatter(x, y, z, c=distances, cmap=cmap, s=size, alpha=alpha)
    
    # Set labels and title
    ax.set_title(title, fontsize=16, color='white')
    
    # Remove axes for minimalist design
    ax.set_axis_off()
    
    # Set equal aspect ratio
    max_range = np.array([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]).max() / 2.0
    mid_x = (x.max()+x.min()) * 0.5
    mid_y = (y.max()+y.min()) * 0.5
    mid_z = (z.max()+z.min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    # Set background color to black
    ax.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
    ax.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
    ax.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
    ax.set_facecolor('black')
    fig.patch.set_facecolor('black')
    
    # Set text color to white
    ax.title.set_color('white')
    
    plt.tight_layout()
    return fig, ax

def create_animation_from_files(file_pattern, output_file="sparc_animation.mp4"):
    """Create an animation from multiple simulation data files"""
    # For now, we'll create a simple animation from the simulation output files
    # In a real implementation, this would read particle positions from binary files
    
    # Read data from one of the output files to get time series
    time, energy, max_r2 = read_simulation_data("simulation_output_electron.txt")
    
    if time is None:
        print("Failed to read simulation data")
        return
    
    # Create figure for animation
    fig = plt.figure(figsize=(12, 10), dpi=200)
    ax = fig.add_subplot(111, projection='3d')
    
    # Create cosmic colormap
    cmap = create_cosmic_cmap()
    
    # Generate some sample particle data for demonstration
    # In a real implementation, this would read actual particle positions
    def update(frame_idx):
        ax.clear()
        
        # Generate sample particle data (in real implementation, read from file)
        n_particles = 1000
        t = frame_idx * 0.1
        x = np.random.uniform(-1, 1, n_particles) * (1 + t)
        y = np.random.uniform(-1, 1, n_particles) * (1 + t)
        z = np.random.uniform(-1, 1, n_particles) * (1 + t)
        
        # Calculate distance from origin for coloring
        distances = np.sqrt(x**2 + y**2 + z**2)
        
        # Create scatter plot with cosmic colors
        scatter = ax.scatter(x, y, z, c=distances, cmap=cmap, s=1, alpha=0.7)
        
        # Add multiple glow layers for artistic effect
        for i in range(3):
            alpha = 0.3 / (i + 1)
            size = 1 + i * 0.5
            ax.scatter(x, y, z, c=distances, cmap=cmap, s=size, alpha=alpha)
        
        ax.set_title(f'SPARC Particle Visualization - Time: {time[min(frame_idx, len(time)-1)]:.2f}', 
                    fontsize=16, color='white')
        
        # Remove axes for minimalist design
        ax.set_axis_off()
        
        # Set equal aspect ratio
        max_range = np.array([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]).max() / 2.0
        mid_x = (x.max()+x.min()) * 0.5
        mid_y = (y.max()+y.min()) * 0.5
        mid_z = (z.max()+z.min()) * 0.5
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        
        # Set background color to black
        ax.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        ax.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        ax.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        
        return ax
    
    # Create animation
    anim = animation.FuncAnimation(fig, update, frames=min(50, len(time)), interval=100, blit=False)
    
    # Save animation
    print(f"Creating animation: {output_file}")
    anim.save(output_file, writer='ffmpeg', fps=10, dpi=200)
    print(f"Animation saved as {output_file}")

def main():
    # Create a static visualization
    print("Creating static visualization...")
    
    # Generate sample particle data for demonstration
    n_particles = 5000
    x = np.random.uniform(-1, 1, n_particles)
    y = np.random.uniform(-1, 1, n_particles)
    z = np.random.uniform(-1, 1, n_particles)
    
    # Filter to create a spherical distribution
    r = np.sqrt(x**2 + y**2 + z**2)
    mask = r <= 1.0
    x, y, z = x[mask], y[mask], z[mask]
    
    fig, ax = visualize_static_particles(x, y, z, "SPARC Particle Visualization", dpi=500)
    plt.savefig("sparc_visualization.png", dpi=500, bbox_inches='tight', facecolor='black')
    plt.show()
    print("Static visualization saved as 'sparc_visualization.png'")
    
    # Create animation
    print("Creating animation...")
    create_animation_from_files("simulation_output_*.txt", "sparc_animation.mp4")

if __name__ == "__main__":
    main()