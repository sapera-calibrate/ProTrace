"""
ProTrace Setup
==============

Setup script for ProTrace protocol package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="protrace",
    version="2.0.0",
    author="Sapera Calibrate",
    author_email="contact@sapera.io",
    description="Zero-Knowledge Digital Asset Verification & NFT Attestation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sapera-calibrate/ProTrace",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security :: Cryptography",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "Pillow>=8.0.0",
        "scipy>=1.7.0",
        "blake3>=0.3.0",
        "iscc-core>=1.0.8",
        "ipfshttpclient>=0.8.0a2",
        "web3>=6.0.0",
        "eth-account>=0.8.0",
        "sha3>=1.0.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "mypy>=0.800",
            "flake8>=3.9.0",
        ],
        "eip712": [
            "sha3>=1.0.0",
            "eth-account>=0.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "protrace=protrace.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
