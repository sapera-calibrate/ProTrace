# ProTrace Rust Makefile
# Convenience commands for building and testing

.PHONY: help build test clean install fmt lint doc example run-test

# Default target
help:
	@echo "ProTrace Rust - Available Commands"
	@echo "=================================="
	@echo "  make build       - Build all crates (debug)"
	@echo "  make release     - Build optimized release"
	@echo "  make test        - Run all tests"
	@echo "  make install     - Install CLI tool"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make fmt         - Format code"
	@echo "  make lint        - Run linter"
	@echo "  make doc         - Generate documentation"
	@echo "  make example     - Run basic usage example"
	@echo "  make run-test    - Run end-to-end test"
	@echo "  make setup       - Setup devnet wallet"

# Build targets
build:
	@echo "Building debug..."
	cargo build

release:
	@echo "Building release..."
	cargo build --release

# Test targets
test:
	@echo "Running tests..."
	cargo test --workspace

test-verbose:
	@echo "Running tests (verbose)..."
	cargo test --workspace -- --nocapture

# Installation
install: release
	@echo "Installing CLI tool..."
	cargo install --path crates/cli --force

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	cargo clean

# Code quality
fmt:
	@echo "Formatting code..."
	cargo fmt --all

fmt-check:
	@echo "Checking format..."
	cargo fmt --all -- --check

lint:
	@echo "Running clippy..."
	cargo clippy --workspace --all-targets -- -D warnings

# Documentation
doc:
	@echo "Generating documentation..."
	cargo doc --workspace --no-deps --open

doc-private:
	@echo "Generating documentation (with private items)..."
	cargo doc --workspace --no-deps --document-private-items --open

# Examples
example:
	@echo "Running basic usage example..."
	cargo run --example basic_usage

# Testing with CLI
run-test:
	@echo "Running end-to-end test..."
	@echo "Note: Requires test images in test_images/"
	cargo run --release --bin protrace -- test test_images/*.png --verbose

# Setup
setup:
	@echo "Setting up devnet..."
	@bash scripts/setup-devnet.sh

# Audit
audit:
	@echo "Checking for vulnerabilities..."
	cargo audit

# All checks before commit
check: fmt-check lint test
	@echo "All checks passed!"

# Quick development cycle
dev:
	@echo "Running development cycle..."
	cargo check
	cargo test --lib
	@echo "Development checks passed!"
