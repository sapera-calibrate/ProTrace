#!/usr/bin/env python3
"""
Check if images can be opened
"""

from PIL import Image
import os

def check_image_opening():
    """Check if the claimed duplicate images can be opened"""

    test_images = [
        "Folder X/# (433).png",
        "tobe_minted/cccc20777.png"
    ]

    for img_path in test_images:
        print(f"\nChecking: {img_path}")

        if not os.path.exists(img_path):
            print("  File does not exist")
            continue

        try:
            with Image.open(img_path) as img:
                print(f"  Format: {img.format}")
                print(f"  Size: {img.size}")
                print(f"  Mode: {img.mode}")
                print("  Can open: ✅")
        except Exception as e:
            print(f"  ERROR opening: {e}")

if __name__ == "__main__":
    check_image_opening()
