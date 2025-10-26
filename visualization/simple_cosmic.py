#!/usr/bin/env python3
"""
Simple SPARC Particle 2D Visualization using Matplotlib
Creates visually stunning, artistic particle visualizations with cosmic color gradients
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap

# Create cosmic colormap
def create_cosmic_cmap():
    """Create a cosmic color gradient colormap"""
    colors = ['black', 'purple', 'blue', 'cyan', 'white']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('cosmic', colors, N=n_bins)
    return cmap

# Generate sample particle data
def generate_sample_data(num_particles=5000):
    """Generate sample particle data for visualization"""
    # Generate particles in a circular distribution
    angles = np.random.uniform(0, 2 * np.pi, num_particles)
    radii = np.random.uniform(0, 1, num_particles)
    
    # Create non-uniform distribution (more dense toward center)
    radii = np.power(radii, 0.5)
    
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    
    return x, y

# Create the visualization
def create_visualization():
    """Create a cosmic particle visualization"""
    # Generate particle data
    x, y = generate_sample_data(5000)
    
    # Create figure with cosmic aesthetics
    fig, ax = plt.subplots(figsize=(12, 12), dpi=500)  # High DPI for stunning visuals
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    
    # Remove axes for minimalist design (as requested)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    # Set limits
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    
    # Create cosmic colormap
    cmap = create_cosmic_cmap()
    
    # Calculate distances for coloring
    distances = np.sqrt(x**2 + y**2)
    
    # Create scatter plot with multiple glow layers (as requested)
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
    
    # Add title with white color for contrast
    ax.set_title('SPARC Particle Simulation - Cosmic Visualization', 
                color='white', fontsize=14, pad=20)
    
    # Save with high DPI for maximum aesthetic impact (as requested)
    plt.tight_layout()
    plt.savefig('sparc_cosmic_visualization.png', dpi=500, bbox_inches='tight', 
                facecolor='black', edgecolor='none')
    
    # Show the plot
    plt.show()
    
    print("Cosmic visualization saved as 'sparc_cosmic_visualization.png'")

def main():
    print("Creating SPARC Cosmic Particle Visualization...")
    print("This visualization features:")
    print("- No grid, no axes (minimalist design)")
    print("- High DPI (500) for stunning visuals")
    print("- Multiple glow layers for artistic effect")
    print("- Cosmic color gradients")
    print("- Central glow effects")
    
    # Create visualization
    create_visualization()
    
    print("Visualization completed!")

if __name__ == "__main__":
    main()