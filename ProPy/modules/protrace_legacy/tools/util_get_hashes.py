#!/usr/bin/env python3
"""
Get full DNA hashes for comparison
"""

import os
from protrace.image_dna import compute_dna

def get_full_hashes():
    """Get full DNA hashes"""

    images = [
        "tobe_minted/cccc20777.png",
        "tobe_minted/ccccc (222).png",
        "tobe_minted/neeed# (1).png",
        "tobe_minted/neeed# (3).png"
    ]

    for img_path in images:
        if os.path.exists(img_path):
            dna_result = compute_dna(img_path)
            dna_hex = dna_result['dna_hex']
            print(f"{os.path.basename(img_path)}: {dna_hex}")

if __name__ == "__main__":
    get_full_hashes()
