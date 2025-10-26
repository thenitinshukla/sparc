#!/usr/bin/env python3
"""
SPARC Real-time OpenGL Animation
Inspired by nbody explosion visualization with cosmic aesthetics
Creates stunning 3D particle animations with trails and glow effects
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import struct
import os
import glob
import sys
from pathlib import Path
import math

# Configuration
class Config:
    WINDOW_SIZE = (1920, 1080)
    FPS = 60
    POINT_SIZE = 3.0
    GLOW_LAYERS = 3
    TRAIL_LENGTH = 20
    CAMERA_DISTANCE = 5.0
    FOV = 45
    ROTATION_SPEED = 0.5
    
    # Colors (cosmic theme)
    BG_COLOR = (0.0, 0.0, 0.05, 1.0)  # Deep space blue-black
    
    @staticmethod
    def get_particle_color(distance, velocity):
        """Generate cosmic color based on distance and velocity"""
        # Normalize distance (0-1)
        d = min(distance / 3.0, 1.0)
        # Normalize velocity magnitude
        v = min(velocity / 2.0, 1.0)
        
        # Color gradient: center (white-yellow) -> middle (cyan-blue) -> outer (purple-red)
        if d < 0.3:
            # Core: White to yellow to orange
            r = 1.0
            g = 1.0 - d * 1.5
            b = 0.3 - d
        elif d < 0.6:
            # Middle: Orange to cyan
            t = (d - 0.3) / 0.3
            r = 1.0 - t * 0.8
            g = 0.5 + t * 0.5
            b = t
        else:
            # Outer: Cyan to blue to purple
            t = (d - 0.6) / 0.4
            r = 0.2 + t * 0.6
            g = 1.0 - t * 0.7
            b = 1.0
        
        # Add velocity-based intensity
        intensity = 0.7 + v * 0.3
        
        return (r * intensity, g * intensity, b * intensity)


class ParticleData:
    """Handle reading and storing particle data"""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.frames = []
        self.current_frame = 0
        self.num_particles = 0
        self.load_data()
    
    def load_data(self):
        """Load particle position data from binary files"""
        # Look for binary position files
        pos_files = sorted(glob.glob(str(self.output_dir / "positions_*.bin")))
        
        if not pos_files:
            print(f"No binary position files found in {self.output_dir}")
            print("Generating sample data...")
            self.generate_sample_data()
            return
        
        print(f"Found {len(pos_files)} position files")
        
        for pos_file in pos_files:
            try:
                with open(pos_file, 'rb') as f:
                    # Read number of particles
                    n_particles = struct.unpack('i', f.read(4))[0]
                    
                    # Read positions
                    positions = []
                    for _ in range(n_particles):
                        x = struct.unpack('d', f.read(8))[0]
                        y = struct.unpack('d', f.read(8))[0]
                        z = struct.unpack('d', f.read(8))[0]
                        positions.append([x, y, z])
                    
                    self.frames.append(np.array(positions, dtype=np.float32))
                    
                    if self.num_particles == 0:
                        self.num_particles = n_particles
            
            except Exception as e:
                print(f"Error reading {pos_file}: {e}")
        
        if self.frames:
            print(f"Loaded {len(self.frames)} frames with {self.num_particles} particles each")
        else:
            print("Failed to load data, generating sample...")
            self.generate_sample_data()
    
    def generate_sample_data(self, num_frames=100, num_particles=5000):
        """Generate sample Coulomb explosion data"""
        print(f"Generating {num_frames} frames with {num_particles} particles")
        
        # Initial uniform distribution in sphere
        theta = np.random.uniform(0, 2*np.pi, num_particles)
        phi = np.arccos(np.random.uniform(-1, 1, num_particles))
        r0 = np.random.uniform(0, 1.0, num_particles) ** (1/3)  # Uniform in volume
        
        x0 = r0 * np.sin(phi) * np.cos(theta)
        y0 = r0 * np.sin(phi) * np.sin(theta)
        z0 = r0 * np.cos(phi)
        
        # Initial velocities (radial outward, proportional to radius)
        vr = r0 * 0.5 + 0.1
        vx = vr * np.sin(phi) * np.cos(theta)
        vy = vr * np.sin(phi) * np.sin(theta)
        vz = vr * np.cos(phi)
        
        # Generate frames
        for frame in range(num_frames):
            t = frame * 0.02
            
            # Simple ballistic expansion
            x = x0 + vx * t
            y = y0 + vy * t
            z = z0 + vz * t
            
            positions = np.column_stack([x, y, z]).astype(np.float32)
            self.frames.append(positions)
        
        self.num_particles = num_particles
        print(f"Sample data generated: {len(self.frames)} frames")
    
    def get_frame(self, frame_idx):
        """Get particle positions for a specific frame"""
        if not self.frames:
            return np.zeros((0, 3), dtype=np.float32)
        
        idx = frame_idx % len(self.frames)
        return self.frames[idx]
    
    def get_num_frames(self):
        return len(self.frames)


class ParticleRenderer:
    """Handle OpenGL rendering of particles"""
    
    def __init__(self, config):
        self.config = config
        self.rotation_x = 0
        self.rotation_y = 0
        self.auto_rotate = True
        self.show_trails = True
        self.trail_history = []
        
    def init_opengl(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        
        glClearColor(*self.config.BG_COLOR)
        
        # Setup projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.config.FOV, 
                      self.config.WINDOW_SIZE[0] / self.config.WINDOW_SIZE[1],
                      0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def setup_camera(self):
        """Setup camera position and rotation"""
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -self.config.CAMERA_DISTANCE)
        
        if self.auto_rotate:
            self.rotation_y += self.config.ROTATION_SPEED
        
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
    
    def render_particles(self, positions, velocities=None):
        """Render particles with glow effects"""
        if len(positions) == 0:
            return
        
        # Calculate distances from origin
        distances = np.linalg.norm(positions, axis=1)
        
        # Calculate velocities if not provided
        if velocities is None:
            velocities = np.zeros(len(positions))
        else:
            velocities = np.linalg.norm(velocities, axis=1)
        
        # Render multiple glow layers
        for layer in range(self.config.GLOW_LAYERS):
            alpha = 0.8 / (layer + 1)
            size = self.config.POINT_SIZE * (1 + layer * 0.5)
            
            glPointSize(size)
            glBegin(GL_POINTS)
            
            for i, pos in enumerate(positions):
                color = self.config.get_particle_color(distances[i], velocities[i])
                glColor4f(color[0], color[1], color[2], alpha)
                glVertex3fv(pos)
            
            glEnd()
        
        # Add central glow
        self.render_central_glow()
    
    def render_central_glow(self):
        """Render glowing center"""
        glPointSize(100.0)
        glBegin(GL_POINTS)
        glColor4f(1.0, 0.9, 0.6, 0.3)
        glVertex3f(0, 0, 0)
        glEnd()
        
        glPointSize(200.0)
        glBegin(GL_POINTS)
        glColor4f(1.0, 0.7, 0.3, 0.15)
        glVertex3f(0, 0, 0)
        glEnd()
    
    def render_trails(self, trail_history):
        """Render particle trails"""
        if not self.show_trails or len(trail_history) < 2:
            return
        
        # Sample particles for trails (every 10th particle to avoid clutter)
        sample_indices = range(0, len(trail_history[0]), 10)
        
        glLineWidth(1.0)
        
        for idx in sample_indices:
            glBegin(GL_LINE_STRIP)
            
            for i, frame_positions in enumerate(trail_history):
                if idx < len(frame_positions):
                    pos = frame_positions[idx]
                    dist = np.linalg.norm(pos)
                    color = self.config.get_particle_color(dist, 0)
                    
                    # Fade older trail positions
                    alpha = (i + 1) / len(trail_history) * 0.3
                    glColor4f(color[0], color[1], color[2], alpha)
                    glVertex3fv(pos)
            
            glEnd()
    
    def render_axes(self, size=2.0):
        """Render coordinate axes for reference"""
        glLineWidth(2.0)
        glBegin(GL_LINES)
        
        # X axis (red)
        glColor4f(1.0, 0.0, 0.0, 0.5)
        glVertex3f(0, 0, 0)
        glVertex3f(size, 0, 0)
        
        # Y axis (green)
        glColor4f(0.0, 1.0, 0.0, 0.5)
        glVertex3f(0, 0, 0)
        glVertex3f(0, size, 0)
        
        # Z axis (blue)
        glColor4f(0.0, 0.0, 1.0, 0.5)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, size)
        
        glEnd()
    
    def render_bounding_sphere(self, radius=1.0):
        """Render initial bounding sphere"""
        glColor4f(0.3, 0.3, 0.5, 0.15)
        glLineWidth(1.0)
        
        # Draw sphere as circle in XY, XZ, YZ planes
        for plane in range(3):
            glBegin(GL_LINE_LOOP)
            for i in range(64):
                angle = 2 * np.pi * i / 64
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                
                if plane == 0:  # XY plane
                    glVertex3f(x, y, 0)
                elif plane == 1:  # XZ plane
                    glVertex3f(x, 0, y)
                else:  # YZ plane
                    glVertex3f(0, x, y)
            glEnd()


class SPARCAnimation:
    """Main animation controller"""
    
    def __init__(self, output_dir):
        self.config = Config()
        self.data = ParticleData(output_dir)
        self.renderer = ParticleRenderer(self.config)
        
        self.current_frame = 0
        self.paused = False
        self.show_info = True
        self.save_screenshots = False
        self.screenshot_counter = 0
        
        pygame.init()
        pygame.display.set_mode(self.config.WINDOW_SIZE, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("SPARC Coulomb Explosion - Real-time Animation")
        
        self.renderer.init_opengl()
        self.clock = pygame.time.Clock()
        
        # Font for HUD
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def handle_events(self):
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    return False
                elif event.key == K_SPACE:
                    self.paused = not self.paused
                elif event.key == K_r:
                    self.renderer.auto_rotate = not self.renderer.auto_rotate
                elif event.key == K_t:
                    self.renderer.show_trails = not self.renderer.show_trails
                elif event.key == K_i:
                    self.show_info = not self.show_info
                elif event.key == K_s:
                    self.save_screenshot()
                elif event.key == K_a:
                    self.save_screenshots = not self.save_screenshots
                elif event.key == K_LEFT:
                    self.current_frame = max(0, self.current_frame - 1)
                elif event.key == K_RIGHT:
                    self.current_frame = min(self.data.get_num_frames() - 1, 
                                            self.current_frame + 1)
                elif event.key == K_HOME:
                    self.current_frame = 0
                elif event.key == K_END:
                    self.current_frame = self.data.get_num_frames() - 1
            
            elif event.type == MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left mouse button
                    dx, dy = event.rel
                    self.renderer.rotation_x += dy * 0.5
                    self.renderer.rotation_y += dx * 0.5
                    self.renderer.auto_rotate = False
        
        # Mouse wheel for zoom
        keys = pygame.key.get_pressed()
        if keys[K_UP] or keys[K_EQUALS]:
            self.config.CAMERA_DISTANCE *= 0.95
        if keys[K_DOWN] or keys[K_MINUS]:
            self.config.CAMERA_DISTANCE *= 1.05
        
        return True
    
    def save_screenshot(self):
        """Save current frame as screenshot"""
        filename = f"sparc_frame_{self.screenshot_counter:04d}.png"
        
        # Read pixels from framebuffer
        x, y, width, height = glGetIntegerv(GL_VIEWPORT)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(x, y, width, height, GL_RGB, GL_UNSIGNED_BYTE)
        
        # Convert to pygame surface and save
        image = pygame.image.fromstring(data, (width, height), "RGB", True)
        pygame.image.save(image, filename)
        
        print(f"Screenshot saved: {filename}")
        self.screenshot_counter += 1
    
    def render_hud(self):
        """Render HUD information"""
        if not self.show_info:
            return
        
        # Create text surface
        info_lines = [
            f"Frame: {self.current_frame + 1}/{self.data.get_num_frames()}",
            f"Particles: {self.data.num_particles}",
            f"FPS: {int(self.clock.get_fps())}",
            f"Paused: {'Yes' if self.paused else 'No'}",
            f"Auto-rotate: {'On' if self.renderer.auto_rotate else 'Off'}",
            f"Trails: {'On' if self.renderer.show_trails else 'Off'}",
        ]
        
        # Create pygame surface for text
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.config.WINDOW_SIZE[0], self.config.WINDOW_SIZE[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        y_offset = 10
        for line in info_lines:
            self.render_text(line, 10, y_offset, self.small_font)
            y_offset += 25
        
        # Controls help
        help_text = [
            "Controls:",
            "SPACE - Pause/Resume",
            "R - Toggle rotation",
            "T - Toggle trails",
            "I - Toggle info",
            "S - Screenshot",
            "← → - Navigate frames",
            "Mouse - Rotate view",
            "+/- - Zoom",
            "ESC - Exit"
        ]
        
        y_offset = self.config.WINDOW_SIZE[1] - 260
        for line in help_text:
            self.render_text(line, 10, y_offset, self.small_font, (0.7, 0.7, 1.0))
            y_offset += 25
        
        glEnable(GL_DEPTH_TEST)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def render_text(self, text, x, y, font, color=(1, 1, 1)):
        """Render text using pygame font"""
        text_surface = font.render(text, True, 
                                   (int(color[0]*255), int(color[1]*255), int(color[2]*255)))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        glRasterPos2f(x, y)
        glDrawPixels(text_surface.get_width(), text_surface.get_height(),
                    GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    def run(self):
        """Main animation loop"""
        print("\n" + "="*60)
        print("SPARC Real-time OpenGL Animation")
        print("="*60)
        print(f"Frames loaded: {self.data.get_num_frames()}")
        print(f"Particles: {self.data.num_particles}")
        print("\nControls:")
        print("  SPACE - Pause/Resume")
        print("  R - Toggle auto-rotation")
        print("  T - Toggle trails")
        print("  I - Toggle info display")
        print("  S - Save screenshot")
        print("  ← → - Navigate frames")
        print("  Mouse drag - Rotate view")
        print("  +/- or UP/DOWN - Zoom")
        print("  ESC - Exit")
        print("="*60 + "\n")
        
        running = True
        
        while running:
            running = self.handle_events()
            
            # Update frame
            if not self.paused:
                self.current_frame = (self.current_frame + 1) % self.data.get_num_frames()
            
            # Get current positions
            positions = self.data.get_frame(self.current_frame)
            
            # Update trail history
            if self.renderer.show_trails:
                self.renderer.trail_history.append(positions.copy())
                if len(self.renderer.trail_history) > self.config.TRAIL_LENGTH:
                    self.renderer.trail_history.pop(0)
            
            # Clear and render
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            self.renderer.setup_camera()
            
            # Render scene
            self.renderer.render_bounding_sphere(1.0)
            self.renderer.render_axes()
            
            if self.renderer.show_trails:
                self.renderer.render_trails(self.renderer.trail_history)
            
            self.renderer.render_particles(positions)
            
            # Render HUD
            self.render_hud()
            
            pygame.display.flip()
            
            # Auto-screenshot if enabled
            if self.save_screenshots and self.current_frame % 5 == 0:
                self.save_screenshot()
            
            self.clock.tick(self.config.FPS)
        
        pygame.quit()
        print("\nAnimation closed")


def main():
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = "../main_sparc_serial/output"
    
    print(f"Loading data from: {output_dir}")
    
    app = SPARCAnimation(output_dir)
    app.run()


if __name__ == "__main__":
    main()
