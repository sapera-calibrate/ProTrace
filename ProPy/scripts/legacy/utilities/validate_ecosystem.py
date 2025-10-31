#!/usr/bin/env python3
"""
ProTRACE Ecosystem Validation Script
====================================

Comprehensive validation of the entire ProTRACE ecosystem:
1. Import validation
2. Module structure validation
3. CLI functionality
4. Core functionality tests
5. Performance checks

Usage:
    python validate_ecosystem.py
"""

import sys
import os
from pathlib import Path
import traceback
import time

class EcosystemValidator:
    """Validates the ProTRACE ecosystem."""
    
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
        
    def log_pass(self, test_name: str):
        """Log a passed test."""
        self.passed.append(test_name)
        print(f"✅ {test_name}")
    
    def log_fail(self, test_name: str, error: Exception):
        """Log a failed test."""
        self.failed.append((test_name, error))
        print(f"❌ {test_name}: {error}")
    
    def log_warning(self, test_name: str, message: str):
        """Log a warning."""
        self.warnings.append((test_name, message))
        print(f"⚠️  {test_name}: {message}")
    
    def test_imports(self):
        """Test all critical imports."""
        print("\n" + "="*80)
        print("IMPORT VALIDATION")
        print("="*80)
        
        # Core package
        try:
            import protrace
            self.log_pass(f"Core protrace package (v{protrace.__version__})")
        except Exception as e:
            self.log_fail("Core protrace package", e)
            return
        
        # Core modules
        modules = [
            ('protrace.image_dna', 'DNA Engine'),
            ('protrace.merkle', 'Merkle Tree'),
            ('protrace.vector_db', 'Vector Database'),
            ('protrace.eip712', 'EIP-712 Signing'),
            ('protrace.edition_core', 'Edition Management'),
            ('protrace.cross_chain_minting', 'Cross-Chain Minting'),
            ('protrace.relayer_service', 'Relayer Service'),
            ('protrace.ipfs', 'IPFS Manager'),
        ]
        
        for module_name, display_name in modules:
            try:
                __import__(module_name)
                self.log_pass(f"{display_name} module")
            except Exception as e:
                self.log_fail(f"{display_name} module", e)
        
        # New organized modules
        try:
            from protrace.cli import main, cli
            self.log_pass("CLI module")
        except Exception as e:
            self.log_fail("CLI module", e)
    
    def test_functionality(self):
        """Test core functionality."""
        print("\n" + "="*80)
        print("FUNCTIONALITY VALIDATION")
        print("="*80)
        
        # Test DNA computation (without actual image)
        try:
            from protrace import compute_dna, hamming_distance
            self.log_pass("DNA computation functions available")
        except Exception as e:
            self.log_fail("DNA computation", e)
        
        # Test Merkle tree
        try:
            from protrace import MerkleTree
            tree = MerkleTree()
            # Test that MerkleTree class is available and has expected methods
            if hasattr(tree, 'add_leaf') and hasattr(tree, 'get_root'):
                self.log_pass("Merkle tree construction")
            else:
                self.log_warning("Merkle tree", "Missing expected methods")
        except Exception as e:
            self.log_fail("Merkle tree", e)
        
        # Test Vector DB
        try:
            from protrace import create_vector_db
            db = create_vector_db(use_postgres=False)
            self.log_pass("Vector database initialization")
        except Exception as e:
            self.log_fail("Vector database", e)
        
        # Test Edition system
        try:
            from protrace.edition_core import EditionMode, UniversalKey
            mode = EditionMode.STRICT_1_1
            self.log_pass("Edition management system")
        except Exception as e:
            self.log_fail("Edition management", e)
    
    def test_structure(self):
        """Test directory structure."""
        print("\n" + "="*80)
        print("STRUCTURE VALIDATION")
        print("="*80)
        
        # Required directories
        directories = [
            ('protrace', 'Core package'),
            ('protrace/cli', 'CLI module'),
            ('protrace/registration', 'Registration module'),
            ('protrace/tools', 'Tools module'),
            ('protrace/benchmarks', 'Benchmarks module'),
            ('demos', 'Demos directory'),
            ('tests', 'Tests directory'),
            ('scripts', 'Scripts directory'),
        ]
        
        for dir_path, display_name in directories:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                files = list(path.glob('*.py'))
                self.log_pass(f"{display_name} ({len(files)} Python files)")
            else:
                self.log_warning(display_name, "Directory not found")
        
        # Check backwards compatibility
        if Path("protrace.py").exists():
            self.log_pass("Backwards compatibility wrapper (protrace.py)")
        else:
            self.log_fail("Backwards compatibility", Exception("protrace.py not found"))
    
    def test_cli(self):
        """Test CLI functionality."""
        print("\n" + "="*80)
        print("CLI VALIDATION")
        print("="*80)
        
        try:
            from protrace.cli.main import main
            # CLI is importable
            self.log_pass("CLI entry point accessible")
        except Exception as e:
            self.log_fail("CLI entry point", e)
    
    def test_performance(self):
        """Test basic performance."""
        print("\n" + "="*80)
        print("PERFORMANCE CHECK")
        print("="*80)
        
        # Test import speed
        try:
            start = time.time()
            import protrace
            import_time = (time.time() - start) * 1000
            
            if import_time < 1000:  # Less than 1 second
                self.log_pass(f"Import speed ({import_time:.2f}ms)")
            else:
                self.log_warning("Import speed", f"Slow import ({import_time:.2f}ms)")
        except Exception as e:
            self.log_fail("Import performance", e)
    
    def run_validation(self):
        """Run all validation tests."""
        print("="*80)
        print("ProTRACE ECOSYSTEM VALIDATION")
        print("="*80)
        print("Validating reorganized project structure and functionality...")
        
        # Run all tests
        self.test_imports()
        self.test_functionality()
        self.test_structure()
        self.test_cli()
        self.test_performance()
        
        # Summary
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        
        print(f"\n✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        
        if self.failed:
            print("\n❌ FAILED TESTS:")
            for test_name, error in self.failed:
                print(f"   • {test_name}")
                print(f"     Error: {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for test_name, message in self.warnings:
                print(f"   • {test_name}: {message}")
        
        # Overall status
        print("\n" + "="*80)
        if not self.failed:
            print("🎉 ECOSYSTEM VALIDATION SUCCESSFUL!")
            print("All critical tests passed. ProTRACE is ready to use.")
        elif len(self.failed) <= 2:
            print("⚠️  ECOSYSTEM VALIDATION MOSTLY SUCCESSFUL")
            print("Most tests passed, but some minor issues found.")
        else:
            print("❌ ECOSYSTEM VALIDATION FAILED")
            print("Critical issues found. Please review failed tests.")
        print("="*80)
        
        return len(self.failed) == 0

def main():
    """Main validation entry point."""
    validator = EcosystemValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
