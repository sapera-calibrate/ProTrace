#!/usr/bin/env python3
"""
Create test images for CLI testing
"""
from PIL import Image
import numpy as np
from pathlib import Path

# Create main test image
print("Creating test image: image.png")
img_array = np.zeros((256, 256, 3), dtype=np.uint8)
img_array[0:128, 0:128] = [255, 0, 0]        # Red
img_array[0:128, 128:256] = [0, 255, 0]      # Green
img_array[128:256, 0:128] = [0, 0, 255]      # Blue
img_array[128:256, 128:256] = [255, 255, 0]  # Yellow
img = Image.fromarray(img_array)
img.save("image.png")
print("✅ Created image.png")

# Create images directory
images_dir = Path("./images")
images_dir.mkdir(exist_ok=True)
print(f"\nCreating test images in: {images_dir}")

# Create 5 different test images
for i in range(5):
    img_array = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    # Add some pattern to make them distinct
    if i == 0:
        img_array[0:128, :] = [255, 0, 0]
    elif i == 1:
        img_array[:, 0:128] = [0, 255, 0]
    elif i == 2:
        img_array[64:192, 64:192] = [0, 0, 255]
    elif i == 3:
        img_array[::2, ::2] = [255, 255, 0]
    else:
        img_array[:, :] = np.random.randint(100, 200, (256, 256, 3), dtype=np.uint8)
    
    img = Image.fromarray(img_array)
    filename = images_dir / f"test_image_{i+1}.png"
    img.save(filename)
    print(f"✅ Created {filename}")

print("\n✅ All test images created!")
print(f"   - image.png (single image test)")
print(f"   - ./images/ (5 images for batch test)")
