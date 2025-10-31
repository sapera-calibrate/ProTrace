#!/usr/bin/env python3
"""
ProTrace System Validation
==========================

Quick validation script to ensure all components are working correctly.
Run this before deploying or after major changes.

Usage: python validate_system.py
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📦 Checking Dependencies...")

    deps_status = {}

    # Core dependencies
    try:
        import PIL
        deps_status['PIL'] = "✅ Available"
    except ImportError:
        deps_status['PIL'] = "❌ Missing"

    try:
        import numpy
        deps_status['numpy'] = "✅ Available"
    except ImportError:
        deps_status['numpy'] = "❌ Missing"

    try:
        import hashlib
        deps_status['hashlib'] = "✅ Available"
    except ImportError:
        deps_status['hashlib'] = "❌ Missing"

    # Print results
    for dep, status in deps_status.items():
        print(f"   {dep}: {status}")

    return all("✅" in status for status in deps_status.values())

def check_directories():
    """Check if required directories exist"""
    print("\n📁 Checking Directories...")

    dirs = ['V_ipfs', 'V_on_chain', 'V_off_chain', 'To_be_minted', 'tests']
    dirs_status = {}

    for dir_name in dirs:
        if Path(dir_name).exists():
            dirs_status[dir_name] = "✅ Exists"
        else:
            dirs_status[dir_name] = "❌ Missing"

    for dir_name, status in dirs_status.items():
        print(f"   {dir_name}/: {status}")

    return all("✅" in status for status in dirs_status.values())

def check_core_functionality():
    """Test core ProTrace functionality"""
    print("\n🧪 Testing Core Functionality...")

    try:
        from protrace import CoreProtocol, MerkleTree
        protocol = CoreProtocol()
        merkle_tree = MerkleTree()

        # Test basic operations
        root = protocol.get_merkle_root()
        merkle_info = protocol.get_merkle_tree_info()

        print("   ✅ CoreProtocol: Imports and initializes")
        print("   ✅ MerkleTree: Creates successfully")
        print(f"   📊 Merkle root: {root[:32]}...")
        print(f"   🌳 Tree info: {merkle_info['leaf_count']} leaves, {merkle_info['tree_depth']} depth")

        return True
    except Exception as e:
        print(f"   ❌ Core functionality error: {e}")
        return False

def check_cli():
    """Test CLI functionality"""
    print("\n💻 Testing CLI...")

    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "protrace.py", "merkle", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("   ✅ CLI: Merkle info command works")
            return True
        else:
            print(f"   ❌ CLI error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ CLI test error: {e}")
        return False

def check_dna():
    """Test UTGMH DNA extraction functionality"""
    print("\n🧬 Testing UTGMH DNA Extraction...")

    try:
        from protrace.image_dna import extract_dna_features
        from PIL import Image

        # Create test image
        img = Image.new('RGB', (64, 64), color='blue')

        # Save temporarily for testing
        test_path = "temp_validation_image.png"
        img.save(test_path)

        # Extract DNA features
        dna_data = extract_dna_features(test_path)

        # Clean up
        if os.path.exists(test_path):
            os.remove(test_path)

        if 'dna_signature' in dna_data and dna_data['dna_signature']:
            print("   ✅ UTGMH: DNA extraction works")
            print(f"   🔗 Generated: {dna_data['dna_signature'][:32]}...")
            return True
        else:
            print("   ❌ UTGMH: DNA extraction failed")
            return False
    except Exception as e:
        print(f"   ❌ UTGMH test error: {e}")
        return False

def main():
    """Run all validation checks"""
    print("🚀 ProTrace System Validation")
    print("=" * 50)

    checks = [
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Core Functionality", check_core_functionality),
        ("CLI", check_cli),
        ("UTGMH DNA", check_dna),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results.append((check_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {check_name}")
        if result:
            passed += 1

    success_rate = (passed / total) * 100

    print(f"\n📈 Results: {passed}/{total} checks passed ({success_rate:.1f}%)")

    if success_rate == 100:
        print("\n🎉 ProTrace system is fully operational!")
        print("   Ready for production deployment.")
        return 0
    elif success_rate >= 80:
        print("\n⚠️  ProTrace system is mostly operational.")
        print("   Some non-critical components may need attention.")
        return 1
    else:
        print("\n❌ ProTrace system has critical issues.")
        print("   Please fix the failing checks before proceeding.")
        return 2

if __name__ == "__main__":
    sys.exit(main())
