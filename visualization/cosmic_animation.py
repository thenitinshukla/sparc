#!/usr/bin/env python3
"""
SPARC Particle 2D Animation using Matplotlib
Creates visually stunning, artistic N-body visualizations with cosmic color gradients
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches

# Create cosmic colormap
def create_cosmic_cmap():
    """Create a cosmic color gradient colormap"""
    colors = ['black', 'purple', 'blue', 'cyan', 'white']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('cosmic', colors, N=n_bins)
    return cmap

# Generate sample particle data
def generate_sample_data(num_particles=3000):
    """Generate sample particle data for visualization"""
    # Generate particles in a circular distribution
    angles = np.random.uniform(0, 2 * np.pi, num_particles)
    radii = np.random.uniform(0, 1, num_particles)
    
    # Create non-uniform distribution (more dense toward center)
    radii = np.power(radii, 0.5)
    
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    
    # Add some velocity for animation
    vx = np.random.uniform(-0.02, 0.02, num_particles)
    vy = np.random.uniform(-0.02, 0.02, num_particles)
    
    return x, y, vx, vy

# Update particle positions
def update_particles(x, y, vx, vy, dt=0.05):
    """Update particle positions with simple physics"""
    # Update positions
    x += vx * dt
    y += vy * dt
    
    # Simple boundary conditions - bounce off edges
    mask_right = x > 1.5
    mask_left = x < -1.5
    mask_top = y > 1.5
    mask_bottom = y < -1.5
    
    vx[mask_right] *= -1
    vx[mask_left] *= -1
    vy[mask_top] *= -1
    vy[mask_bottom] *= -1
    
    x = np.clip(x, -1.5, 1.5)
    y = np.clip(y, -1.5, 1.5)
    
    return x, y, vx, vy

# Create the animation
def create_animation():
    """Create a cosmic particle animation"""
    # Generate initial particle data
    x, y, vx, vy = generate_sample_data(3000)
    
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
    def animate(frame):
        nonlocal x, y, vx, vy
        
        # Update particles
        x, y, vx, vy = update_particles(x, y, vx, vy, 0.05)
        
        # Calculate distances for coloring
        distances = np.sqrt(x**2 + y**2)
        
        # Update scatter plot
        scatter.set_offsets(np.column_stack((x, y)))
        scatter.set_array(distances)
        
        # Update central glow
        central_glow.set_alpha(0.2 + 0.1 * np.sin(frame * 0.1))
        
        # Update title with frame info
        title.set_text(f'SPARC Particle Simulation - Frame {frame}')
        
        return scatter, central_glow, title
    
    # Create animation
    anim = FuncAnimation(fig, animate, frames=500, interval=50, blit=True, repeat=True)
    
    # Show the animation
    plt.tight_layout()
    plt.show()
    
    return anim

# Save animation as MP4
def save_animation(anim, filename='sparc_cosmic_animation.mp4'):
    """Save the animation as an MP4 file"""
    print(f"Saving animation as {filename}...")
    anim.save(filename, writer='ffmpeg', fps=20, dpi=100)
    print(f"Animation saved as {filename}")

def main():
    print("Creating SPARC Cosmic Particle Animation...")
    print("Close the window to exit or let it run to create MP4")
    
    # Create animation
    anim = create_animation()
    
    # Optionally save as MP4 (uncomment the next line if you want to save)
    # save_animation(anim, 'sparc_cosmic_animation.mp4')
    
    print("Animation completed!")

if __name__ == "__main__":
    main()