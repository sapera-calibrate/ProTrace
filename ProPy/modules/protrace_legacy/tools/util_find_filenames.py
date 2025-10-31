#!/usr/bin/env python3
"""
Find the actual filename for each image index
"""

import os
import json

def find_actual_filenames():
    """Find which actual filenames correspond to the indices"""

    # Get all images in Folder X in the same order as dna_merkle_benchmark.py would process them
    folder = "Folder X"
    extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

    images = []
    for f in os.listdir(folder):
        if f.lower().endswith(extensions):
            images.append(f)

    # Sort them to see the order (os.listdir() order may vary)
    print(f"Found {len(images)} images")
    print("First 10 images in directory order:")
    for i, img in enumerate(images[:10]):
        print(f"  {i}: {img}")

    print("
Images 430-440:")
    for i in range(430, min(441, len(images))):
        print(f"  {i}: {images[i]}")

    # Check the specific indices that were claimed to match
    claimed_indices = [433, 450, 511, 517]
    print("
Claimed matching indices:")
    for idx in claimed_indices:
        if idx < len(images):
            print(f"  image_{idx} -> {images[idx]}")
        else:
            print(f"  image_{idx} -> INDEX OUT OF RANGE")

if __name__ == "__main__":
    find_actual_filenames()
