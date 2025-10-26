#!/usr/bin/env python3
"""
SPARC Particle 2D Animation using pyOpenGL
Creates visually stunning, artistic N-body visualizations with cosmic color gradients
"""

import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys
import os
import time

# Initialize pygame and OpenGL
def init():
    pygame.init()
    display = (1000, 1000)
    pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("SPARC Particle Simulation - Cosmic Visualization")
    
    # Set up OpenGL
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Set up 2D orthographic projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-1.5, 1.5, -1.5, 1.5)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Enable blending for transparency effects
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Point smoothing for better-looking particles
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

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
    
    # Add some velocity for animation
    vx = np.random.uniform(-0.01, 0.01, num_particles)
    vy = np.random.uniform(-0.01, 0.01, num_particles)
    
    return x, y, vx, vy

# Update particle positions
def update_particles(x, y, vx, vy, dt=0.01):
    """Update particle positions with simple physics"""
    # Update positions
    x += vx * dt
    y += vy * dt
    
    # Simple boundary conditions - wrap around
    x = np.where(x > 1.5, x - 3.0, x)
    x = np.where(x < -1.5, x + 3.0, x)
    y = np.where(y > 1.5, y - 3.0, y)
    y = np.where(y < -1.5, y + 3.0, y)
    
    return x, y

# Render particles with cosmic aesthetics
def render_particles(x, y, time_value=0):
    """Render particles with cosmic visual effects"""
    
    # Clear screen
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Calculate distances from center for coloring
    distances = np.sqrt(x**2 + y**2)
    
    # Normalize distances for coloring (0 to 1)
    max_dist = np.max(distances)
    if max_dist > 0:
        normalized_distances = distances / max_dist
    else:
        normalized_distances = distances
    
    # Draw multiple glow layers for artistic effect
    for layer in range(3):
        # Layer-specific parameters
        size_factor = 1.0 + layer * 0.3
        alpha_factor = 1.0 / (layer + 1) * 0.5
        
        # Set point size
        glPointSize(2.0 * size_factor)
        
        # Draw particles for this layer
        glBegin(GL_POINTS)
        for i in range(len(x)):
            # Calculate color based on distance (cosmic gradient)
            dist = normalized_distances[i]
            
            # Create cosmic color gradient (purple -> blue -> cyan -> white)
            if dist < 0.25:
                # Purple to blue
                r = 0.5 * (1.0 - dist * 4)
                g = 0.0
                b = 0.5 + dist * 2
            elif dist < 0.5:
                # Blue to cyan
                r = 0.0
                g = (dist - 0.25) * 4
                b = 1.0
            elif dist < 0.75:
                # Cyan to white
                r = (dist - 0.5) * 4
                g = 1.0
                b = 1.0
            else:
                # White with slight tint
                r = 1.0
                g = 1.0
                b = 1.0 - (dist - 0.75) * 2
            
            # Add time-based color variation for dynamic effect
            color_time = time_value * 0.5
            r = max(0, min(1, r + 0.1 * math.sin(color_time + i * 0.01)))
            g = max(0, min(1, g + 0.1 * math.sin(color_time * 1.3 + i * 0.015)))
            b = max(0, min(1, b + 0.1 * math.sin(color_time * 0.7 + i * 0.012)))
            
            # Set color with alpha
            glColor4f(r, g, b, 0.7 * alpha_factor)
            
            # Draw point
            glVertex2f(x[i], y[i])
        
        glEnd()
    
    # Draw central glow effect
    glPointSize(50.0)
    glBegin(GL_POINTS)
    glColor4f(1.0, 1.0, 0.8, 0.3)  # Soft yellow glow
    glVertex2f(0.0, 0.0)
    glEnd()
    
    glPointSize(100.0)
    glBegin(GL_POINTS)
    glColor4f(1.0, 0.8, 0.4, 0.2)  # Outer glow
    glVertex2f(0.0, 0.0)
    glEnd()

# Main animation loop
def main():
    # Initialize OpenGL
    init()
    
    # Generate initial particle data
    x, y, vx, vy = generate_sample_data(3000)
    
    # Animation parameters
    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    
    print("Starting SPARC 2D Particle Animation")
    print("Press ESC or close window to exit")
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update particles
        x, y = update_particles(x, y, vx, vy, 0.02)
        
        # Render particles
        render_particles(x, y, int(frame_count * 0.05))
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(60)
        frame_count += 1
        
        # Print status every 60 frames
        if frame_count % 60 == 0:
            print(f"Frame: {frame_count}, FPS: {clock.get_fps():.1f}")
    
    # Clean up
    pygame.quit()
    print("Animation finished")

if __name__ == "__main__":
    main()