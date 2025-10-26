#!/usr/bin/env python3
"""
SPARC Particle GIF Creator
Creates an animated GIF from the generated frames
"""

import os
import glob
from PIL import Image

def create_gif_from_frames(frame_dir='animation_frames', output_file='sparc_animation.gif', duration=200):
    """Create an animated GIF from frames"""
    
    # Get all frame files
    frame_files = sorted(glob.glob(os.path.join(frame_dir, "frame_*.png")))
    
    if not frame_files:
        print(f"No frame files found in {frame_dir}")
        return
    
    print(f"Found {len(frame_files)} frames for GIF creation")
    
    # Open all frames
    frames = []
    for frame_file in frame_files:
        frame = Image.open(frame_file)
        frames.append(frame)
    
    # Create animated GIF
    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0
    )
    
    print(f"Animated GIF saved as {output_file}")

def main():
    import sys
    
    # Default values
    frame_dir = 'animation_frames'
    output_file = 'sparc_animation.gif'
    duration = 200  # milliseconds per frame
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        frame_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        duration = int(sys.argv[3])
    
    create_gif_from_frames(frame_dir, output_file, duration)

if __name__ == "__main__":
    main()