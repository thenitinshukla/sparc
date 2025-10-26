#!/usr/bin/env python3
"""
Simple SPARC Particle 2D Animation using pyOpenGL
Creates visually stunning, artistic particle visualizations
"""

import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys
import os

# Initialize pygame and OpenGL
def init():
    pygame.init()
    display = (800, 800)
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
def render_particles(x, y):
    """Render particles with cosmic visual effects"""
    
    # Clear screen
    glClear(GL_COLOR_BUFFER_BIT)
    
    # Draw particles with cosmic colors
    glBegin(GL_POINTS)
    glColor4f(0.2, 0.6, 1.0, 0.8)  # Blue-cyan particles
    glPointSize(3.0)
    
    for i in range(len(x)):
        glVertex2f(x[i], y[i])
    
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
        render_particles(x, y)
        
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