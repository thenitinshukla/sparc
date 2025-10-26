import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

def test_animation_files():
    """Test that animation files exist and are not empty"""
    animation_files = [
        "high_quality_sparc_animation.gif",
        "simple_sparc_animation.gif",
        "combined_sparc_animation.gif",
        "advanced_sparc_animation.gif"
    ]
    
    print("Testing animation files:")
    print("=" * 50)
    
    for file in animation_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✓ {file}: {size} bytes")
            
            # Try to load the image to check if it's valid
            try:
                img = mpimg.imread(file)
                print(f"  - Successfully loaded, shape: {img.shape}")
            except Exception as e:
                print(f"  - Error loading: {e}")
        else:
            print(f"✗ {file}: Not found")
        print()

if __name__ == "__main__":
    test_animation_files()