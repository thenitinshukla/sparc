#!/usr/bin/env python3
"""
SPARC Benchmark Runner
Runs and compares all SPARC implementations
"""

import subprocess
import time
import os
import sys
import json
import numpy as np
from datetime import datetime

class SPARCBenchmark:
    def __init__(self, results_dir="results"):
        self.results_dir = results_dir
        self.implementations = {
            'python': {
                'command': 'python pythonsparc/main.py',
                'output': 'pythonsparc/python_output/energy_vs_time.txt'
            },
            'serial': {
                'command': 'bin/sparc_serial.exe input_file.txt -s',
                'output': 'output/simulation_output_electron.txt'
            },
            'optimized': {
                'command': 'bin/sparc_optimized.exe input_file.txt -s',
                'output': 'output/simulation_output_electron.txt'
            },
            'fastmath': {
                'command': 'bin/sparc_fastmath.exe input_file.txt -s',
                'output': 'output/simulation_output_electron.txt'
            },
            'parallel': {
                'command': 'bin/sparc_parallel.exe input_file.txt -s',
                'output': 'output/simulation_output_electron.txt'
            }
        }
        
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
    
    def run_benchmark(self, name, config):
        """Run a single benchmark"""
        print(f"\n{'='*80}")
        print(f"Running: {name}")
        print(f"{'='*80}")
        
        # Clean previous output
        if name != 'python' and os.path.exists(config['output']):
            os.remove(config['output'])
        
        # Run and time
        start_time = time.time()
        try:
            result = subprocess.run(
                config['command'],
                shell=True,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            elapsed_time = time.time() - start_time
            
            if result.returncode != 0:
                print(f"ERROR: {name} failed")
                print(result.stderr)
                return None
                
        except subprocess.TimeoutExpired:
            print(f"ERROR: {name} timed out")
            return None
        except FileNotFoundError:
            print(f"ERROR: {name} executable not found")
            return None
        
        # Parse results
        try:
            energy_data = self.parse_energy_data(name, config['output'])
        except Exception as e:
            print(f"ERROR: Failed to parse results: {e}")
            return None
        
        benchmark_results = {
            'name': name,
            'elapsed_time': elapsed_time,
            'energy_data': energy_data,
            'stdout': result.stdout,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✓ Completed in {elapsed_time:.3f} seconds")
        
        return benchmark_results
    
    def parse_energy_data(self, name, output_file):
        """Parse energy data from output file"""
        if name == 'python':
            data = np.loadtxt(output_file, skiprows=1)
            return {
                'time': data[:, 0].tolist(),
                'energy': data[:, 1].tolist(),
                'initial_energy': float(data[0, 1]),
                'final_energy': float(data[-1, 1]),
                'energy_drift': float((data[-1, 1] - data[0, 1]) / data[0, 1] * 100)
            }
        else:
            data = np.loadtxt(output_file, delimiter=',', skiprows=1)
            return {
                'time': data[:, 0].tolist(),
                'energy': data[:, 1].tolist(),
                'initial_energy': float(data[0, 1]),
                'final_energy': float(data[-1, 1]),
                'energy_drift': float((data[-1, 1] - data[0, 1]) / data[0, 1] * 100),
                'num_particles': int(data[0, 3])
            }
    
    def run_all_benchmarks(self):
        """Run all benchmarks"""
        results = {}
        
        for name, config in self.implementations.items():
            result = self.run_benchmark(name, config)
            if result:
                results[name] = result
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.results_dir, f"benchmark_{timestamp}.json")
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_file}")
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def print_summary(self, results):
        """Print benchmark summary"""
        print(f"\n{'='*80}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*80}")
        
        if not results:
            print("No results to display")
            return
        
        # Find reference (Python)
        ref_time = results.get('python', {}).get('elapsed_time', 0)
        ref_energy = results.get('python', {}).get('energy_data', {}).get('initial_energy', 0)
        
        print(f"\n{'Implementation':<15} {'Time (s)':<12} {'Speedup':<10} {'Energy':<15} {'Drift %':<10}")
        print("-" * 80)
        
        for name, result in sorted(results.items()):
            time_val = result['elapsed_time']
            speedup = ref_time / time_val if time_val > 0 else 0
            energy = result['energy_data']['initial_energy']
            drift = result['energy_data']['energy_drift']
            
            print(f"{name:<15} {time_val:<12.3f} {speedup:<10.2f}x {energy:<15.6e} {drift:<10.6f}")
        
        print(f"\n{'='*80}")
        
        # Accuracy comparison
        print("\nACCURACY COMPARISON (vs Python)")
        print("-" * 80)
        
        for name, result in sorted(results.items()):
            if name == 'python':
                continue
            
            cpp_energy = result['energy_data']['initial_energy']
            diff = abs(cpp_energy - ref_energy) / ref_energy * 100
            
            status = "✓ PASS" if diff < 1.0 else "⚠ WARN"
            print(f"{name:<15} Energy diff: {diff:>8.4f}% {status}")
        
        print(f"{'='*80}\n")


def main():
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║                    SPARC BENCHMARK SUITE                                ║
    ║           Spherical Plasma Coulomb Explosion Simulation                 ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    benchmark = SPARCBenchmark()
    results = benchmark.run_all_benchmarks()
    
    print("\n✓ Benchmarking complete!")
    

if __name__ == "__main__":
    main()
