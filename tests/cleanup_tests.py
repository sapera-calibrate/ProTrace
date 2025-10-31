#!/usr/bin/env python3
"""
Cleanup script to remove test files and sprite files
"""

import os
import shutil
from pathlib import Path

# Directories and files to remove
ITEMS_TO_REMOVE = [
    # ProPy test files
    "ProPy/tests",
    "ProPy/testsprite_tests",
    "ProPy/scripts/create_test_images.py",
    
    # ProRust test files
    "ProRust/tests",
    
    # TestSprite documentation
    "TESTSPRITE_QUICK_START.md",
    "TESTSPRITE_TESTING_GUIDE.md",
    
    # TestSprite config files
    "shared/config/testsprite.config.json",
    "shared/config/testsprite_endpoints.json",
    "shared/docs/TESTSPRITE_GUIDE.md",
    
    # Other test artifacts
    "testsprite_api_endpoints.json",
    "API_ENDPOINTS_FOR_TESTING.md",
]

def cleanup():
    """Remove test and sprite files"""
    base_dir = Path(__file__).parent
    removed = []
    skipped = []
    
    print("🧹 Cleaning up test and sprite files...\n")
    
    for item in ITEMS_TO_REMOVE:
        item_path = base_dir / item
        
        if item_path.exists():
            try:
                if item_path.is_dir():
                    shutil.rmtree(item_path)
                    removed.append(f"📁 {item}")
                else:
                    item_path.unlink()
                    removed.append(f"📄 {item}")
            except Exception as e:
                skipped.append(f"⚠️  {item} - {str(e)}")
        else:
            skipped.append(f"⏭️  {item} (not found)")
    
    # Print results
    print("✅ REMOVED:")
    for item in removed:
        print(f"  {item}")
    
    if skipped:
        print("\n⚠️  SKIPPED:")
        for item in skipped:
            print(f"  {item}")
    
    print(f"\n📊 Summary: {len(removed)} removed, {len(skipped)} skipped")
    print("✅ Cleanup complete!")

if __name__ == "__main__":
    cleanup()
