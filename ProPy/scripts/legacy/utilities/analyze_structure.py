#!/usr/bin/env python3
"""
Analyze and categorize all Python files in the ProTRACE project.
"""

import os
from pathlib import Path
from collections import defaultdict

def analyze_project_structure():
    """Analyze and categorize all Python files."""
    
    project_root = Path(".")
    
    # Categories for classification
    categories = {
        'core_modules': [],       # Already in protrace/
        'demos': [],              # Demo scripts
        'tests': [],              # Test files
        'utilities': [],          # Utility scripts
        'benchmarks': [],         # Performance benchmarks
        'registration': [],       # Registration related
        'verification': [],       # Verification related
        'debugging': [],          # Debug scripts
        'standalone': [],         # Standalone tools
    }
    
    # Files to analyze (root level Python files)
    root_files = [
        'batch_register.py',
        'check_images.py',
        'check_registry_entries.py',
        'create_correct_duplicates.py',
        'create_duplicates_folder.py',
        'debug_hashes.py',
        'debug_registry.py',
        'demo_edition_management.py',
        'demo_registration.py',
        'dna_merkle_benchmark.py',
        'find_actual_filenames.py',
        'find_matches.py',
        'get_full_hashes.py',
        'merkle_benchmark.py',
        'merkle_benchmark_simple.py',
        'protrace.py',
        'register_image.py',
        'test_batch_logic.py',
        'test_determinism.py',
        'test_dna.py',
        'test_registration.py',
        'verify_correct_matches.py',
        'verify_folder_x.py',
    ]
    
    print("="*80)
    print("ProTRACE Project Structure Analysis")
    print("="*80)
    
    # Categorize files
    for filename in root_files:
        filepath = project_root / filename
        if not filepath.exists():
            continue
            
        # Read first few lines to understand purpose
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read(500)  # First 500 chars
        except:
            content = ""
        
        # Categorize based on name and content
        if filename.startswith('demo_'):
            categories['demos'].append(filename)
        elif filename.startswith('test_'):
            categories['tests'].append(filename)
        elif 'benchmark' in filename:
            categories['benchmarks'].append(filename)
        elif 'register' in filename or 'batch_register' in filename:
            categories['registration'].append(filename)
        elif 'verify' in filename or 'check' in filename:
            categories['verification'].append(filename)
        elif 'debug' in filename:
            categories['debugging'].append(filename)
        elif filename == 'protrace.py':
            categories['core_modules'].append(filename)
        else:
            categories['utilities'].append(filename)
    
    # Print categorization
    print("\n📁 FILE CATEGORIZATION")
    print("-"*80)
    
    for category, files in categories.items():
        if files:
            print(f"\n{category.upper().replace('_', ' ')} ({len(files)} files):")
            for f in sorted(files):
                print(f"  • {f}")
    
    # Directory structure
    print("\n\n📂 CURRENT DIRECTORY STRUCTURE")
    print("-"*80)
    
    dirs_to_check = [
        'protrace/',
        'SSC/',
        'Perceptual Hashing Engine/',
        'demos/',
        'scripts/',
        'tests/',
        'V_on_chain/',
        'registry/',
        'zk-system/',
        'poseidon-merkle-zk/',
        'merkle_zk_demo/',
    ]
    
    for dir_name in dirs_to_check:
        dir_path = project_root / dir_name
        if dir_path.exists():
            py_files = list(dir_path.glob('*.py'))
            print(f"\n{dir_name} ({len(py_files)} Python files)")
            for f in sorted(py_files):
                print(f"  • {f.name}")
    
    # Recommendations
    print("\n\n💡 REORGANIZATION RECOMMENDATIONS")
    print("-"*80)
    
    recommendations = [
        {
            'action': 'Create protrace/demos/ submodule',
            'files': categories['demos'],
            'reason': 'Consolidate demo scripts for better organization'
        },
        {
            'action': 'Create protrace/cli/ submodule',
            'files': ['protrace.py'],
            'reason': 'Separate CLI interface from core modules'
        },
        {
            'action': 'Create protrace/tools/ submodule',
            'files': categories['utilities'] + categories['verification'] + categories['debugging'],
            'reason': 'Utility and debugging tools in one place'
        },
        {
            'action': 'Create protrace/benchmarks/ submodule',
            'files': categories['benchmarks'],
            'reason': 'Performance testing and benchmarks'
        },
        {
            'action': 'Move to tests/ directory',
            'files': categories['tests'],
            'reason': 'Consolidate all test files'
        },
        {
            'action': 'Create protrace/registration/ submodule',
            'files': categories['registration'],
            'reason': 'Registration-related functionality'
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        if rec['files']:
            print(f"\n{i}. {rec['action']}")
            print(f"   Reason: {rec['reason']}")
            print(f"   Files ({len(rec['files'])}):")
            for f in rec['files'][:5]:  # Show first 5
                print(f"     • {f}")
            if len(rec['files']) > 5:
                print(f"     ... and {len(rec['files'])-5} more")
    
    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)
    
    return categories

if __name__ == "__main__":
    analyze_project_structure()
