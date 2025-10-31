#!/usr/bin/env python3
"""
ProTrace Performance Monitor
============================

Comprehensive performance monitoring and profiling tool for ProTrace components.

Features:
- CPU and memory usage monitoring
- Function-level profiling
- Benchmarking of key operations
- Performance regression detection
- Resource usage analysis

Usage:
    python perf_monitor.py [command] [options]

Commands:
    monitor     - Real-time performance monitoring
    profile     - Profile specific functions
    benchmark   - Run performance benchmarks
    compare     - Compare performance across runs
    report      - Generate performance report
"""

import time
import psutil
import os
import json
import argparse
from datetime import datetime
from functools import wraps
from typing import Dict, List, Any, Optional
import statistics
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from protrace import CoreProtocol, setup_logging
    logger = setup_logging()
except ImportError as e:
    print(f"Warning: Could not import ProTrace: {e}")
    logger = None

class PerformanceMonitor:
    """Performance monitoring and profiling tool"""

    def __init__(self, log_dir: str = "perf_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.metrics = {}
        self.start_time = None

    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.metrics = {
            'cpu_percent': [],
            'memory_percent': [],
            'memory_mb': [],
            'disk_io': [],
            'network_io': [],
            'timestamps': []
        }

        # Get initial system info
        self.initial_cpu = psutil.cpu_percent(interval=None)
        self.initial_memory = psutil.virtual_memory()

        logger.info("Performance monitoring started")

    def record_metrics(self):
        """Record current system metrics"""
        if not self.start_time:
            return

        timestamp = time.time() - self.start_time

        self.metrics['timestamps'].append(timestamp)
        self.metrics['cpu_percent'].append(psutil.cpu_percent(interval=0.1))
        self.metrics['memory_percent'].append(psutil.virtual_memory().percent)
        self.metrics['memory_mb'].append(psutil.virtual_memory().used / 1024 / 1024)

        # Disk I/O (if available)
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.metrics['disk_io'].append({
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes
                })
        except:
            pass

        # Network I/O (if available)
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                self.metrics['network_io'].append({
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv
                })
        except:
            pass

    def stop_monitoring(self) -> Dict:
        """Stop monitoring and return collected metrics"""
        if not self.start_time:
            return {}

        duration = time.time() - self.start_time

        # Calculate summary statistics
        summary = {
            'duration_seconds': duration,
            'avg_cpu_percent': statistics.mean(self.metrics['cpu_percent']) if self.metrics['cpu_percent'] else 0,
            'max_cpu_percent': max(self.metrics['cpu_percent']) if self.metrics['cpu_percent'] else 0,
            'avg_memory_percent': statistics.mean(self.metrics['memory_percent']) if self.metrics['memory_percent'] else 0,
            'max_memory_percent': max(self.metrics['memory_percent']) if self.metrics['memory_percent'] else 0,
            'peak_memory_mb': max(self.metrics['memory_mb']) if self.metrics['memory_mb'] else 0,
            'total_samples': len(self.metrics['timestamps'])
        }

        # Save detailed metrics
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.log_dir / f"perf_metrics_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                'summary': summary,
                'detailed': self.metrics,
                'timestamp': timestamp
            }, f, indent=2)

        logger.info(".2f")
        return summary

def timed_with_monitoring(func):
    """Decorator that combines timing with system monitoring"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        monitor = PerformanceMonitor()

        # Start monitoring
        monitor.start_monitoring()

        start_time = time.time()

        try:
            # Run function
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            success = False
            raise e
        finally:
            execution_time = time.time() - start_time

            # Stop monitoring
            perf_summary = monitor.stop_monitoring()

            # Log results
            if logger:
                logger.info(f"Function {func.__name__} completed in {execution_time:.4f}s")
                logger.info(f"Performance: CPU {perf_summary.get('avg_cpu_percent', 0):.1f}%, "
                          f"Memory {perf_summary.get('avg_memory_percent', 0):.1f}%")

        return result
    return wrapper

class BenchmarkSuite:
    """Suite of performance benchmarks"""

    def __init__(self):
        self.results = {}
        self.monitor = PerformanceMonitor()

    def benchmark_registration(self, iterations: int = 10) -> Dict:
        """Benchmark asset registration performance"""
        print(f"Running registration benchmark ({iterations} iterations)...")

        if not logger:
            print("Skipping registration benchmark - ProTrace not available")
            return {}

        protocol = CoreProtocol()

        # Create test image if it doesn't exist
        test_image = "test_image.png"
        if not Path(test_image).exists():
            # Create a simple test image
            try:
                from PIL import Image
                img = Image.new('RGB', (100, 100), color='blue')
                img.save(test_image)
            except ImportError:
                print("PIL not available, skipping registration benchmark")
                return {}

        times = []
        memory_usage = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}")

            start_time = time.time()
            start_memory = psutil.virtual_memory().used

            try:
                fingerprint = protocol.register_asset(test_image, f"test_creator_{i}")
                success = True
            except Exception as e:
                print(f"    Error in iteration {i+1}: {e}")
                success = False

            end_time = time.time()
            end_memory = psutil.virtual_memory().used

            if success:
                times.append(end_time - start_time)
                memory_usage.append((end_memory - start_memory) / 1024 / 1024)  # MB

        # Clean up
        Path(test_image).unlink(missing_ok=True)

        if times:
            result = {
                'operation': 'asset_registration',
                'iterations': iterations,
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'std_time': statistics.stdev(times) if len(times) > 1 else 0,
                'avg_memory_delta_mb': statistics.mean(memory_usage),
                'total_time': sum(times)
            }
        else:
            result = {'operation': 'asset_registration', 'error': 'No successful iterations'}

        self.results['registration'] = result
        return result

    def benchmark_verification(self, iterations: int = 10) -> Dict:
        """Benchmark asset verification performance"""
        print(f"Running verification benchmark ({iterations} iterations)...")

        if not logger:
            print("Skipping verification benchmark - ProTrace not available")
            return {}

        protocol = CoreProtocol()

        # First register an asset
        test_image = "test_verify_image.png"
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(test_image)

            fingerprint = protocol.register_asset(test_image, "test_creator")
            asset_id = fingerprint.asset_id
        except ImportError:
            print("PIL not available, skipping verification benchmark")
            return {}
        except Exception as e:
            print(f"Failed to register test asset: {e}")
            return {}

        times = []
        memory_usage = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}")

            start_time = time.time()
            start_memory = psutil.virtual_memory().used

            try:
                result = protocol.verify_asset(test_image, asset_id)
                success = result.status == "Original"
            except Exception as e:
                print(f"    Error in iteration {i+1}: {e}")
                success = False

            end_time = time.time()
            end_memory = psutil.virtual_memory().used

            if success:
                times.append(end_time - start_time)
                memory_usage.append((end_memory - start_memory) / 1024 / 1024)  # MB

        # Clean up
        Path(test_image).unlink(missing_ok=True)

        if times:
            result = {
                'operation': 'asset_verification',
                'iterations': iterations,
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'std_time': statistics.stdev(times) if len(times) > 1 else 0,
                'avg_memory_delta_mb': statistics.mean(memory_usage),
                'total_time': sum(times)
            }
        else:
            result = {'operation': 'asset_verification', 'error': 'No successful iterations'}

        self.results['verification'] = result
        return result

    def benchmark_merkle_operations(self, iterations: int = 10) -> Dict:
        """Benchmark Merkle tree operations"""
        print(f"Running Merkle operations benchmark ({iterations} iterations)...")

        if not logger:
            return {}

        protocol = CoreProtocol()

        # Register some assets first
        test_image = "test_merkle_image.png"
        try:
            from PIL import Image
            img = Image.new('RGB', (50, 50), color='green')
            img.save(test_image)

            # Register multiple assets
            asset_ids = []
            for i in range(5):
                fingerprint = protocol.register_asset(test_image, f"merkle_creator_{i}")
                asset_ids.append(fingerprint.asset_id)

        except ImportError:
            print("PIL not available, skipping Merkle benchmark")
            return {}
        except Exception as e:
            print(f"Failed to register test assets: {e}")
            return {}

        times = []

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}")

            start_time = time.time()

            try:
                # Test Merkle operations
                root = protocol.get_merkle_root()
                proof = protocol.get_merkle_proof(asset_ids[0])
                if proof:
                    is_valid = protocol.verify_merkle_proof(asset_ids[0], proof, root)
                else:
                    is_valid = False
                success = is_valid
            except Exception as e:
                print(f"    Error in iteration {i+1}: {e}")
                success = False

            end_time = time.time()

            if success:
                times.append(end_time - start_time)

        # Clean up
        Path(test_image).unlink(missing_ok=True)

        if times:
            result = {
                'operation': 'merkle_operations',
                'iterations': iterations,
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'std_time': statistics.stdev(times) if len(times) > 1 else 0,
                'total_time': sum(times)
            }
        else:
            result = {'operation': 'merkle_operations', 'error': 'No successful iterations'}

        self.results['merkle'] = result
        return result

    def run_all_benchmarks(self) -> Dict:
        """Run all benchmarks"""
        print("Starting ProTrace Performance Benchmarks")
        print("=" * 50)

        start_time = time.time()

        self.benchmark_registration()
        self.benchmark_verification()
        self.benchmark_merkle_operations()

        total_time = time.time() - start_time

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.monitor.log_dir / f"benchmark_results_{timestamp}.json"

        results_summary = {
            'timestamp': timestamp,
            'total_duration': total_time,
            'results': self.results
        }

        with open(filename, 'w') as f:
            json.dump(results_summary, f, indent=2)

        print(f"\nBenchmarks completed in {total_time:.2f}s")
        print(f"Results saved to: {filename}")

        return results_summary

    def print_results(self):
        """Print benchmark results"""
        print("\nBenchmark Results:")
        print("=" * 50)

        for operation, result in self.results.items():
            if 'error' in result:
                print(f"❌ {operation}: {result['error']}")
                continue

            print(f"✅ {operation}:")
            print(".4f")
            print(".4f")
            print(".4f")
            if 'avg_memory_delta_mb' in result:
                print(".2f")
            print()

def main():
    parser = argparse.ArgumentParser(description="ProTrace Performance Monitor")
    parser.add_argument('command', choices=['monitor', 'profile', 'benchmark', 'report'],
                       help='Command to run')
    parser.add_argument('--duration', type=int, default=60,
                       help='Monitoring duration in seconds (default: 60)')
    parser.add_argument('--iterations', type=int, default=10,
                       help='Number of benchmark iterations (default: 10)')
    parser.add_argument('--output', type=str,
                       help='Output file for results')

    args = parser.parse_args()

    if args.command == 'monitor':
        print(f"Starting performance monitoring for {args.duration} seconds...")
        monitor = PerformanceMonitor()

        monitor.start_monitoring()

        for i in range(args.duration):
            monitor.record_metrics()
            time.sleep(1)
            if i % 10 == 0:
                print(f"Monitoring... {i}/{args.duration}s")

        results = monitor.stop_monitoring()

        print("\nMonitoring Results:")
        print(f"Duration: {results['duration_seconds']:.2f}s")
        print(f"Average CPU: {results['avg_cpu_percent']:.1f}%")
        print(f"Peak CPU: {results['max_cpu_percent']:.1f}%")
        print(f"Average Memory: {results['avg_memory_percent']:.1f}%")
        print(f"Peak Memory: {results['max_memory_percent']:.1f}%")
        print(f"Peak Memory Usage: {results['peak_memory_mb']:.0f} MB")

    elif args.command == 'benchmark':
        suite = BenchmarkSuite()
        results = suite.run_all_benchmarks()
        suite.print_results()

    elif args.command == 'profile':
        print("Profiling functionality not yet implemented")
        print("Use Python's cProfile for detailed profiling:")
        print("python -m cProfile -s time perf_monitor.py benchmark")

    elif args.command == 'report':
        print("Performance reporting functionality not yet implemented")
        print("Check perf_logs/ directory for saved metrics and results")

if __name__ == "__main__":
    main()
