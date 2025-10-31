#!/usr/bin/env python3
"""
ProTRACE Repository Cleanup and Organization
Removes test artifacts and organizes code for production
"""

import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Files to remove (test artifacts, duplicates, old servers)
FILES_TO_REMOVE = [
    # Old API servers (replaced by backend/api.py)
    "api_server.py",
    "api_server_complete.py",
    "api_server_with_testing.py",
    "api_testing_endpoints.py",
    "start_api.py",
    "start_complete_api.py",
    
    # Test mock servers
    "testsprite_mock_server.py",
    "test_server_complete.py",
    "start_test_server.py",
    "start_testsprite_server.bat",
    
    # Test artifacts
    "test_api_client.py",
    "testsprite_compatibility_tests.py",
    "run_testsprite.py",
    "create_test_images.py",
    "test_image.png",
    "test_image2.png",
    
    # Old documentation (consolidated)
    "API_ENDPOINTS_FOR_TESTING.md",
    "CONNECTION_FIX_SUMMARY.md",
    "CONNECTION_REFUSED_FIX.md",
    "ECOSYSTEM_REBUILD_COMPLETE.md",
    "MISSION_ACCOMPLISHED.md",
    "README_TESTING_APIS.md",
    "TESTING_APIS_COMPLETE.md",
    "TESTING_API_DOCUMENTATION.md",
    "TESTING_COMPLETE.md",
    "TESTING_QUICK_START.md",
    "TESTSPRITE_CONFIGURATION_FIX.md",
    "TESTSPRITE_MOCK_SERVER.md",
    "TESTSPRITE_SERVER_READY.md",
    "TESTSPRITE_SUMMARY.md",
    "TEST_SERVER_COMPLETE.md",
    "TEST_SERVER_DOCUMENTATION.md",
    "UPDATED_API_ENDPOINTS.md",
    
    # Test configs
    "testsprite_api_endpoints.json",
    "testsprite_compatibility_results.json",
    "testsprite_endpoints_fixed.json",
]

# Directories to remove (test artifacts)
DIRS_TO_REMOVE = [
    "test_images",
    "test-results",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
]

# Directories to keep
DIRS_TO_KEEP = [
    "backend",
    "protrace",
    "protrace-rust",
    "solana-program",
    "V_on_chain",
    "crates",
    "programs",
    "tests",  # Keep actual tests
    "scripts",
    "data",
    "registry",
    "merkle_nodes",
    "archive",
]

# Files to keep
FILES_TO_KEEP = [
    "README.md",
    "requirements.txt",
    "setup.py",
    "Dockerfile",
    "Dockerfile.zk",
    "docker-compose.yml",
    "Cargo.toml",
    "Cargo.lock",
    "Anchor.toml",
    "package.json",
    "package-lock.json",
    ".dockerignore",
    "deploy.sh",
    "deploy_devnet.sh",
    "cleanup_and_organize.py",
]


def backup_repository():
    """Create backup before cleanup"""
    logger.info("Creating backup...")
    
    project_root = Path.cwd()
    backup_dir = project_root.parent / f"ProTRACE_backup_{int(os.path.getmtime('.'))}"
    
    try:
        shutil.copytree(project_root, backup_dir, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', 'node_modules', '.git'
        ))
        logger.info(f"Backup created: {backup_dir}")
        return True
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False


def remove_files():
    """Remove unnecessary files"""
    logger.info("Removing unnecessary files...")
    
    removed_count = 0
    for file_name in FILES_TO_REMOVE:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Removed: {file_name}")
                removed_count += 1
            except Exception as e:
                logger.warning(f"Could not remove {file_name}: {e}")
    
    logger.info(f"Removed {removed_count} files")


def remove_directories():
    """Remove unnecessary directories"""
    logger.info("Removing unnecessary directories...")
    
    removed_count = 0
    for dir_name in DIRS_TO_REMOVE:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            try:
                shutil.rmtree(dir_path)
                logger.info(f"Removed directory: {dir_name}")
                removed_count += 1
            except Exception as e:
                logger.warning(f"Could not remove {dir_name}: {e}")
    
    logger.info(f"Removed {removed_count} directories")


def organize_tests():
    """Organize test files"""
    logger.info("Organizing tests...")
    
    tests_dir = Path("tests")
    if not tests_dir.exists():
        tests_dir.mkdir()
    
    # Move testsprite_tests content to tests/testsprite
    testsprite_src = Path("testsprite_tests")
    testsprite_dst = tests_dir / "testsprite"
    
    if testsprite_src.exists() and not testsprite_dst.exists():
        try:
            shutil.move(str(testsprite_src), str(testsprite_dst))
            logger.info("Organized TestSprite tests")
        except Exception as e:
            logger.warning(f"Could not organize TestSprite tests: {e}")


def create_directory_structure():
    """Ensure proper directory structure exists"""
    logger.info("Creating directory structure...")
    
    directories = [
        "backend",
        "backend/routers",
        "backend/services",
        "backend/models",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/testsprite",
        "docs",
        "logs",
        "data",
        "registry",
        "merkle_nodes",
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py for Python packages
        if dir_path.startswith("backend") or dir_path.startswith("tests"):
            init_file = Path(dir_path) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    logger.info("Directory structure created")


def generate_gitignore():
    """Generate comprehensive .gitignore"""
    logger.info("Generating .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
test-results/

# Logs
*.log
logs/

# Data & Registry
data/registry/
data/merkle/
registry/*.json
merkle_nodes/*.json

# Environment
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
npm-debug.log
yarn-error.log

# Rust
target/
Cargo.lock

# Solana
.anchor/
target/
test-ledger/

# Backups
*.bak
*_backup/

# Temporary
*.tmp
temp/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    logger.info(".gitignore generated")


def print_summary():
    """Print cleanup summary"""
    logger.info("\n" + "=" * 60)
    logger.info("CLEANUP SUMMARY")
    logger.info("=" * 60)
    
    # Count remaining files
    all_files = list(Path(".").rglob("*"))
    py_files = list(Path(".").rglob("*.py"))
    
    logger.info(f"Total files: {len([f for f in all_files if f.is_file()])}")
    logger.info(f"Python files: {len(py_files)}")
    logger.info(f"Directories: {len([d for d in all_files if d.is_dir()])}")
    
    logger.info("\nCoreDirectories:")
    for dir_name in DIRS_TO_KEEP:
        dir_path = Path(dir_name)
        if dir_path.exists():
            file_count = len(list(dir_path.rglob("*")))
            logger.info(f"  {dir_name}: {file_count} items")
    
    logger.info("\n" + "=" * 60)
    logger.info("Repository is now organized and ready for production!")
    logger.info("=" * 60)


def main():
    """Main cleanup process"""
    logger.info("Starting ProTRACE repository cleanup...")
    logger.info("=" * 60)
    
    # Confirm
    response = input("This will remove test files and reorganize the repo. Create backup? (y/n): ")
    if response.lower() == 'y':
        if not backup_repository():
            logger.error("Backup failed. Aborting cleanup.")
            return
    
    # Execute cleanup
    remove_files()
    remove_directories()
    organize_tests()
    create_directory_structure()
    generate_gitignore()
    
    # Summary
    print_summary()
    
    logger.info("\nNext steps:")
    logger.info("1. Review changes: git status")
    logger.info("2. Start backend: python3 -m backend.api")
    logger.info("3. Run tests: python3 backend/testsprite_runner.py")
    logger.info("4. Deploy to devnet: bash deploy_devnet.sh")


if __name__ == "__main__":
    main()
