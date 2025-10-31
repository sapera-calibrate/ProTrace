#!/usr/bin/env python3
"""
ProTRACE Project Reorganization Script
======================================

Systematically reorganizes the ProTRACE project structure by:
1. Moving scattered Python files into proper modules
2. Creating clean module structure
3. Updating imports
4. Backing up original files

Usage:
    python reorganize_project.py --dry-run  # Preview changes
    python reorganize_project.py --execute  # Execute reorganization
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

class ProjectReorganizer:
    """Handles the reorganization of the ProTRACE project."""
    
    def __init__(self, project_root: Path, dry_run: bool = True):
        self.project_root = project_root
        self.dry_run = dry_run
        self.backup_dir = project_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.moved_files = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        symbol = symbols.get(level, "•")
        print(f"[{timestamp}] {symbol} {message}")
    
    def backup_file(self, filepath: Path):
        """Create a backup of the file."""
        if not self.dry_run and filepath.exists():
            relative_path = filepath.relative_to(self.project_root)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(filepath, backup_path)
            self.log(f"Backed up: {relative_path}", "INFO")
    
    def move_file(self, source: Path, dest: Path):
        """Move a file from source to destination."""
        if not source.exists():
            self.log(f"Source file not found: {source}", "WARNING")
            return False
        
        relative_source = source.relative_to(self.project_root)
        relative_dest = dest.relative_to(self.project_root)
        
        if self.dry_run:
            self.log(f"Would move: {relative_source} → {relative_dest}", "INFO")
        else:
            # Backup original
            self.backup_file(source)
            
            # Create destination directory
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(source), str(dest))
            self.log(f"Moved: {relative_source} → {relative_dest}", "SUCCESS")
            
            self.moved_files.append((relative_source, relative_dest))
        
        return True
    
    def create_directory(self, dirpath: Path):
        """Create a directory."""
        if self.dry_run:
            self.log(f"Would create directory: {dirpath.relative_to(self.project_root)}", "INFO")
        else:
            dirpath.mkdir(parents=True, exist_ok=True)
            self.log(f"Created directory: {dirpath.relative_to(self.project_root)}", "SUCCESS")
    
    def reorganize(self):
        """Execute the full reorganization."""
        self.log("="*70)
        self.log("ProTRACE Project Reorganization")
        self.log("="*70)
        
        if self.dry_run:
            self.log("DRY RUN MODE - No files will be moved", "WARNING")
        else:
            self.log("EXECUTION MODE - Files will be moved", "WARNING")
            self.create_directory(self.backup_dir)
        
        self.log("")
        
        # Phase 1: Create new directories
        self.log("Phase 1: Creating new directory structure...", "INFO")
        self.create_directory(self.project_root / "protrace" / "cli")
        self.create_directory(self.project_root / "protrace" / "registration")
        self.create_directory(self.project_root / "protrace" / "tools")
        self.create_directory(self.project_root / "protrace" / "benchmarks")
        self.log("")
        
        # Phase 2: Move CLI file
        self.log("Phase 2: Moving CLI module...", "INFO")
        self.move_file(
            self.project_root / "protrace.py",
            self.project_root / "protrace" / "cli" / "main.py"
        )
        self.log("")
        
        # Phase 3: Move registration files
        self.log("Phase 3: Moving registration module...", "INFO")
        registration_files = [
            "batch_register.py",
            "register_image.py"
        ]
        for filename in registration_files:
            self.move_file(
                self.project_root / filename,
                self.project_root / "protrace" / "registration" / filename
            )
        self.log("")
        
        # Phase 4: Move utility/tool files
        self.log("Phase 4: Moving utility/tool files...", "INFO")
        
        # Verification tools
        verification_files = {
            "check_images.py": "verification_check_images.py",
            "check_registry_entries.py": "verification_check_registry.py",
            "verify_correct_matches.py": "verification_matches.py",
            "verify_folder_x.py": "verification_folder.py"
        }
        for source, dest in verification_files.items():
            self.move_file(
                self.project_root / source,
                self.project_root / "protrace" / "tools" / dest
            )
        
        # Debug tools
        debug_files = {
            "debug_hashes.py": "debug_hashes.py",
            "debug_registry.py": "debug_registry.py"
        }
        for source, dest in debug_files.items():
            self.move_file(
                self.project_root / source,
                self.project_root / "protrace" / "tools" / dest
            )
        
        # General utilities
        utility_files = {
            "create_correct_duplicates.py": "util_create_duplicates.py",
            "create_duplicates_folder.py": "util_duplicates_folder.py",
            "find_actual_filenames.py": "util_find_filenames.py",
            "find_matches.py": "util_find_matches.py",
            "get_full_hashes.py": "util_get_hashes.py"
        }
        for source, dest in utility_files.items():
            self.move_file(
                self.project_root / source,
                self.project_root / "protrace" / "tools" / dest
            )
        self.log("")
        
        # Phase 5: Move benchmark files
        self.log("Phase 5: Moving benchmark files...", "INFO")
        benchmark_files = {
            "dna_merkle_benchmark.py": "dna_benchmark.py",
            "merkle_benchmark.py": "merkle_benchmark.py",
            "merkle_benchmark_simple.py": "merkle_benchmark_simple.py"
        }
        for source, dest in benchmark_files.items():
            self.move_file(
                self.project_root / source,
                self.project_root / "protrace" / "benchmarks" / dest
            )
        self.log("")
        
        # Phase 6: Move demo files
        self.log("Phase 6: Moving demo files...", "INFO")
        demo_files = {
            "demo_edition_management.py": "edition_demo.py",
            "demo_registration.py": "registration_demo.py"
        }
        for source, dest in demo_files.items():
            self.move_file(
                self.project_root / source,
                self.project_root / "demos" / dest
            )
        self.log("")
        
        # Phase 7: Move test files
        self.log("Phase 7: Moving test files...", "INFO")
        test_files = [
            "test_batch_logic.py",
            "test_determinism.py",
            "test_dna.py",
            "test_registration.py"
        ]
        for filename in test_files:
            self.move_file(
                self.project_root / filename,
                self.project_root / "tests" / filename
            )
        self.log("")
        
        # Summary
        self.log("="*70)
        if self.dry_run:
            self.log("DRY RUN COMPLETE - No files were actually moved", "INFO")
        else:
            self.log(f"REORGANIZATION COMPLETE - {len(self.moved_files)} files moved", "SUCCESS")
            self.log(f"Backup created at: {self.backup_dir.relative_to(self.project_root)}", "INFO")
        self.log("="*70)
        
        # Save report
        if not self.dry_run:
            self.save_report()
    
    def save_report(self):
        """Save reorganization report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "backup_directory": str(self.backup_dir.relative_to(self.project_root)),
            "files_moved": [
                {"from": str(src), "to": str(dest)}
                for src, dest in self.moved_files
            ]
        }
        
        report_file = self.project_root / "reorganization_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Report saved to: {report_file.name}", "SUCCESS")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ProTRACE Project Reorganization")
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without actually moving files')
    parser.add_argument('--execute', action='store_true',
                       help='Execute the reorganization')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("❌ Error: Must specify either --dry-run or --execute")
        parser.print_help()
        return
    
    project_root = Path(__file__).parent
    reorganizer = ProjectReorganizer(project_root, dry_run=args.dry_run)
    reorganizer.reorganize()

if __name__ == "__main__":
    main()
