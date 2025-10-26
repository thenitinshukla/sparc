#!/usr/bin/env python3
"""
Simple SPARC Particle Visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
import os

def generate_sample_data():
    """Generate sample particle data for visualization"""
    # Generate sample particle data
    n_particles = 5000
    x = np.random.uniform(-1, 1, n_particles)
    y = np.random.uniform(-1, 1, n_particles)
    z = np.random.uniform(-1, 1, n_particles)
    
    # Filter to create a spherical distribution
    r = np.sqrt(x**2 + y**2 + z**2)
    mask = r <= 1.0
    x, y, z = x[mask], y[mask], z[mask]
    
    return x, y, z

def create_visualization():
    """Create a 3D visualization of particles"""
    # Generate sample data
    x, y, z = generate_sample_data()
    
    # Create 3D plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create scatter plot
    ax.scatter(x, y, z, c='blue', s=1, alpha=0.7)
    
    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('SPARC Particle Visualization')
    
    # Set equal aspect ratio
    max_range = np.array([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]).max() / 2.0
    mid_x = (x.max()+x.min()) * 0.5
    mid_y = (y.max()+y.min()) * 0.5
    mid_z = (z.max()+z.min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    plt.tight_layout()
    plt.savefig("sparc_visualization.png", dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Visualization saved as 'sparc_visualization.png'")

def main():
    create_visualization()

if __name__ == "__main__":
    main()