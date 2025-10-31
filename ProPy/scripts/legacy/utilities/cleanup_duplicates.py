#!/usr/bin/env python3
"""
Cleanup Duplicates Script
Removes duplicate files that have been archived/reorganized
CAUTION: Run this only after verifying everything works!
"""

import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent

print("⚠️  ProTRACE Duplicate File Cleanup")
print("=" * 60)
print("This will DELETE original files that have been archived/reorganized.")
print("Make sure you've verified everything works before proceeding!")
print()

response = input("Do you want to continue? (yes/NO): ")
if response.lower() != "yes":
    print("Aborted. No files were deleted.")
    exit(0)

print("\n🗑️  Starting cleanup...")

# Files/folders to delete (now that they're archived)
TO_DELETE = [
    # Large archived files
    "backup_20251017_083857",
    "benchmark_registry.json",
    "benchmark_results.json",
    "merkle_tree.json",
    
    # Archived docs
    "REORGANIZATION_PLAN.md",
    "REORGANIZATION_SUMMARY.md",
    "reorganization_report.json",
    "TEST_RUN_RESULTS.md",
    "MERKLE_DNA_TEST_SUMMARY.txt",
    "completion_summary.txt",
    
    # Moved scripts (now in scripts/utilities/)
    "analyze_structure.py",
    "create_duplicates_folder.py",
    "reorganize_project.py",
    "validate_ecosystem.py",
    
    # Moved tests (now in tests/)
    "test_core_functionality.py",
    "test_imports.py",
    "test_merkle_dna_final.py",
    "test_merkle_dna_simple.py",
    "test_reorganization.py",
    "run_benchmarks.py",
    "run_all_tests.py",
    
    # Duplicated docs (now in docs/)
    "QUICKSTART_V2.md",  # Now docs/guides/QUICKSTART.md
    "QUICK_REFERENCE.md",  # Now docs/guides/QUICK_REFERENCE.md
    "REGISTRATION_GUIDE.md",  # Now docs/guides/REGISTRATION_GUIDE.md
    "FINAL_REPORT.md",  # Now docs/specifications/FINAL_REPORT.md
    
    # Duplicated Docker files (now in docker/)
    # KEEP THESE IN ROOT FOR CONVENIENCE
    # "Dockerfile",
    # "Dockerfile.zk",
    # "docker-compose.yml",
    # ".dockerignore",
    
    # Reorganization scripts (completed)
    "reorganize_final.py",
    "REORGANIZATION_PLAN_FINAL.md",
    
    # Empty/test folders
    "Folder X",
    "src",
]

deleted_count = 0
failed_count = 0
total_size_freed = 0

for item in TO_DELETE:
    item_path = BASE_DIR / item
    
    if not item_path.exists():
        print(f"   ⊘ Skip (not found): {item}")
        continue
    
    try:
        if item_path.is_dir():
            # Calculate size before deletion
            size = sum(f.stat().st_size for f in item_path.rglob('*') if f.is_file())
            shutil.rmtree(item_path)
            print(f"   ✓ Deleted folder: {item} ({size / (1024*1024):.2f} MB)")
        else:
            size = item_path.stat().st_size
            item_path.unlink()
            print(f"   ✓ Deleted file: {item} ({size / 1024:.2f} KB)")
        
        deleted_count += 1
        total_size_freed += size
        
    except Exception as e:
        print(f"   ✗ Failed to delete {item}: {e}")
        failed_count += 1

print()
print("=" * 60)
print(f"✅ Cleanup complete!")
print(f"   Deleted: {deleted_count} items")
print(f"   Failed: {failed_count} items")
print(f"   Space freed: {total_size_freed / (1024*1024):.2f} MB")
print()
print("📝 Remaining cleanup (manual):")
print("   1. Review and delete empty __pycache__ folders")
print("   2. Review and delete .pytest_cache")
print("   3. Consider archiving data/ folder if not needed")
print("   4. Run: git clean -fd (to remove untracked files)")

print()
print("🔍 Verification:")
print("   1. Run tests: pytest tests/")
print("   2. Check imports: python -m protrace")
print("   3. Build Rust: cd protrace-rust && cargo build")
