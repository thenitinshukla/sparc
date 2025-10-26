#!/usr/bin/env python3
"""
SPARC Comprehensive Results Comparison Script
Compares outputs from all implementations for correctness validation
and adds runtime, bandwidth, and GFLOPs analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import struct
import sys
import argparse
import warnings

# Suppress specific runtime warnings for plotting
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")


class SPARCComparator:
    """Compare results from different SPARC implementations"""

    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.implementations = {
            'python': self.base_dir.parent / 'pythonsparc' / 'python_output',
            'serial': self.base_dir.parent / 'main_sparc_serial' / 'output',
            'std': self.base_dir.parent / 'sparc_std' / 'output',
            'memorypool': self.base_dir.parent / 'sparc_memoryPool' / 'output',
            'parallel': self.base_dir.parent / 'sparc_parallel' / 'output',
            'parunseq': self.base_dir.parent / 'sparc_parunseq' / 'output',
        }

        self.results = {}
        self.comparison_data = {}

    def read_binary_positions(self, filename):
        """Read particle positions from binary file"""
        try:
            with open(filename, 'rb') as f:
                n_particles = struct.unpack('i', f.read(4))[0]
                positions = np.zeros((n_particles, 3))
                for i in range(n_particles):
                    positions[i, 0] = struct.unpack('d', f.read(8))[0]
                    positions[i, 1] = struct.unpack('d', f.read(8))[0]
                    positions[i, 2] = struct.unpack('d', f.read(8))[0]
                return positions
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return None

    def read_simulation_output(self, filename):
        """Read simulation output file (time, energy, max_r2, runtime, memory, flops)"""
        try:
            data = np.loadtxt(filename, delimiter=',', skiprows=1)
            # Expecting columns: time, energy, max_r2, runtime, memory (GB), flops
            return {
                'time': data[:, 0],
                'energy': data[:, 1],
                'max_r2': data[:, 2],
                'runtime': data[:, 3] if data.shape[1] > 3 else np.nan,
                'memory': data[:, 4] if data.shape[1] > 4 else np.nan,
                'flops': data[:, 5] if data.shape[1] > 5 else np.nan
            }
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return None

    def load_all_implementations(self):
        """Load data from all available implementations"""
        print("="*80)
        print("Loading data from all implementations...")
        print("="*80)

        for name, output_dir in self.implementations.items():
            if not output_dir.exists():
                print(f"  {name:15s}: NOT FOUND - {output_dir}")
                continue

            print(f"  {name:15s}: Loading from {output_dir}")
            sim_files = list(output_dir.glob("simulation_output_*.txt"))
            pos_files = sorted(output_dir.glob("positions_*.bin"))

            if sim_files:
                sim_data = self.read_simulation_output(sim_files[0])
                if sim_data:
                    self.results[name] = {
                        'simulation': sim_data,
                        'positions': []
                    }
                    if pos_files:
                        final_pos = self.read_binary_positions(pos_files[-1])
                        if final_pos is not None and np.all(np.isfinite(final_pos)):
                            self.results[name]['final_positions'] = final_pos
                            print(f"    → Loaded: {len(sim_data['time'])} timesteps, "
                                  f"{len(final_pos)} particles")
                        else:
                            print(f"    → Loaded: {len(sim_data['time'])} timesteps "
                                  f"(position data invalid)")
                    else:
                        print(f"    → Loaded: {len(sim_data['time'])} timesteps (no position data)")
            else:
                print(f"    → No simulation output found")

        print(f"\nSuccessfully loaded {len(self.results)} implementations")
        return len(self.results) > 0

    def compare_energy_conservation(self):
        """Compare energy conservation across implementations"""
        print("\n" + "="*80)
        print("ENERGY CONSERVATION COMPARISON")
        print("="*80)

        energy_errors = {}

        for name, data in self.results.items():
            if 'simulation' in data:
                energy = data['simulation']['energy']
                if len(energy) > 0 and np.isfinite(energy).all():
                    E0 = energy[0]
                    E_final = energy[-1]
                    error = abs(E_final - E0) / abs(E0) * 100
                    energy_errors[name] = error
                    print(f"{name:15s}: Initial={E0:12.6e}, Final={E_final:12.6e}, "
                          f"Error={error:8.5f}%")

        self.comparison_data['energy_errors'] = energy_errors

        if len(energy_errors) > 0:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            names = list(energy_errors.keys())
            errors = list(energy_errors.values())
            colors = ['green' if e < 0.001 else 'orange' if e < 0.01 else 'red' for e in errors]
            ax1.barh(names, errors, color=colors, edgecolor='black')
            ax1.set_xlabel('Energy Conservation Error (%)', fontsize=12)
            ax1.set_title('Energy Conservation Comparison', fontsize=14, fontweight='bold')
            ax1.axvline(x=0.001, color='green', linestyle='--', label='Excellent (<0.001%)', linewidth=2)
            ax1.axvline(x=0.01, color='orange', linestyle='--', label='Good (<0.01%)', linewidth=2)
            ax1.set_xscale('log')
            ax1.legend()
            ax1.grid(axis='x', alpha=0.3)

            for name, data in self.results.items():
                if 'simulation' in data:
                    time = data['simulation']['time']
                    energy = data['simulation']['energy']
                    if len(energy) > 0 and np.isfinite(energy).all():
                        E0 = energy[0]
                        rel_energy = (energy - E0) / abs(E0) * 100
                        ax2.plot(time, rel_energy, label=name, linewidth=2)

            ax2.set_xlabel('Time', fontsize=12)
            ax2.set_ylabel('Relative Energy Error (%)', fontsize=12)
            ax2.set_title('Energy Evolution Over Time', fontsize=14, fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(self.base_dir / 'energy_comparison.png', dpi=300, bbox_inches='tight')
            print(f"\n  → Plot saved: {self.base_dir / 'energy_comparison.png'}")

    def compare_final_positions(self, reference='serial'):
        """Compare final particle positions between implementations"""
        print("\n" + "="*80)
        print("FINAL POSITIONS COMPARISON")
        print("="*80)

        if reference not in self.results or 'final_positions' not in self.results[reference]:
            print(f"Reference implementation '{reference}' not available or has no position data")
            return

        ref_positions = self.results[reference]['final_positions']
        print(f"Using '{reference}' as reference ({len(ref_positions)} particles)")

        position_errors = {}

        for name, data in self.results.items():
            if name == reference or 'final_positions' not in data:
                continue

            positions = data['final_positions']
            if len(positions) != len(ref_positions):
                print(f"  {name:15s}: Particle count mismatch "
                      f"({len(positions)} vs {len(ref_positions)})")
                continue

            diff = positions - ref_positions
            l2_error = np.linalg.norm(diff, axis=1)
            if not np.all(np.isfinite(l2_error)):
                print(f"  {name:15s}: Invalid values in position differences")
                continue

            max_error = np.max(l2_error)
            mean_error = np.mean(l2_error)
            position_errors[name] = {'max': max_error, 'mean': mean_error, 'std': np.std(l2_error)}

            print(f"  {name:15s}: Max={max_error:10.6e}, Mean={mean_error:10.6e}, "
                  f"Std={np.std(l2_error):10.6e}")

        self.comparison_data['position_errors'] = position_errors

        if len(position_errors) > 0:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            names = list(position_errors.keys())
            max_errors = [position_errors[n]['max'] for n in names]
            mean_errors = [position_errors[n]['mean'] for n in names]
            x = np.arange(len(names))
            width = 0.35

            ax1.bar(x - width/2, max_errors, width, label='Max Error', color='coral', edgecolor='black')
            ax1.bar(x + width/2, mean_errors, width, label='Mean Error', color='skyblue', edgecolor='black')
            ax1.set_xticks(x)
            ax1.set_xticklabels(names, rotation=45, ha='right')
            ax1.set_ylabel('Position Error (L2 norm)', fontsize=12)
            ax1.set_title('Final Particle Position Errors', fontsize=14, fontweight='bold')
            ax1.legend()
            ax1.grid(True, axis='y', alpha=0.3)

            # Boxplot of per-particle differences
            all_diffs = [np.linalg.norm(self.results[n]['final_positions'] - ref_positions, axis=1)
                         for n in names]
            ax2.boxplot(all_diffs, labels=names, patch_artist=True,
                        boxprops=dict(facecolor='skyblue', color='black'),
                        medianprops=dict(color='red', linewidth=2))
            ax2.set_ylabel('Per-particle Position Error (L2 norm)', fontsize=12)
            ax2.set_title('Distribution of Final Position Errors', fontsize=14, fontweight='bold')
            ax2.grid(True, axis='y', alpha=0.3)

            plt.tight_layout()
            plt.savefig(self.base_dir / 'position_comparison.png', dpi=300, bbox_inches='tight')
            print(f"\n  → Plot saved: {self.base_dir / 'position_comparison.png'}")

    def plot_runtime_bandwidth_gflops(self):
        """Plot total runtime, bandwidth, and GFLOPs"""
        print("\n" + "="*80)
        print("PERFORMANCE ANALYSIS")
        print("="*80)

        runtimes = {}
        bandwidths = {}
        gflops_per_sec = {}
        memory_usage = {}

        for name, data in self.results.items():
            sim = data['simulation']
            runtime = np.nanmax(sim['runtime'])
            mem = np.nanmax(sim['memory'])
            flops = np.nanmax(sim['flops'])

            if np.isnan(runtime) or runtime <= 0:
                continue

            runtimes[name] = runtime
            memory_usage[name] = mem
            bandwidths[name] = mem / runtime  # GB/sec
            gflops_per_sec[name] = flops / runtime / 1e9  # GFLOPs/sec

        # Runtime vs Allocator
        plt.figure(figsize=(10, 6))
        names = list(runtimes.keys())
        times = [runtimes[n] for n in names]
        plt.bar(names, times, color='skyblue', edgecolor='black')
        plt.ylabel('Runtime (seconds)', fontsize=12)
        plt.title('Total Execution Time per Implementation', fontsize=14, fontweight='bold')
        plt.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.base_dir / 'runtime_comparison.png', dpi=300, bbox_inches='tight')
        print(f"  → Runtime plot saved: {self.base_dir / 'runtime_comparison.png'}")

        # Bandwidth GB/sec
        plt.figure(figsize=(10, 6))
        bw = [bandwidths[n] for n in names]
        plt.bar(names, bw, color='coral', edgecolor='black')
        plt.ylabel('Bandwidth (GB/sec)', fontsize=12)
        plt.title('Memory Bandwidth per Implementation', fontsize=14, fontweight='bold')
        plt.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.base_dir / 'bandwidth_comparison.png', dpi=300, bbox_inches='tight')
        print(f"  → Bandwidth plot saved: {self.base_dir / 'bandwidth_comparison.png'}")

        # GFLOPs/sec vs Memory
        plt.figure(figsize=(10, 6))
        gflops = [gflops_per_sec[n] for n in names]
        mems = [memory_usage[n] for n in names]
        plt.scatter(mems, gflops, s=100, c='green', edgecolor='black')
        for i, n in enumerate(names):
            plt.text(mems[i], gflops[i]*1.01, n, ha='center', fontsize=9)
        plt.xlabel('Memory Usage (GB)', fontsize=12)
        plt.ylabel('GFLOPs/sec', fontsize=12)
        plt.title('GFLOPs/sec vs Memory Usage', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.base_dir / 'gflops_vs_memory.png', dpi=300, bbox_inches='tight')
        print(f"  → GFLOPs vs Memory plot saved: {self.base_dir / 'gflops_vs_memory.png'}")


def main():
    parser = argparse.ArgumentParser(description="Compare SPARC simulation results across implementations")
    parser.add_argument('output_dir', type=str, help='Directory containing output data')
    parser.add_argument('--ref', type=str, default='serial', help='Reference implementation for positions')
    args = parser.parse_args()

    comparator = SPARCComparator(args.output_dir)
    if comparator.load_all_implementations():
        comparator.compare_energy_conservation()
        comparator.compare_final_positions(reference=args.ref)
        comparator.plot_runtime_bandwidth_gflops()
    else:
        print("No implementations loaded. Exiting.")


if __name__ == "__main__":
    main()

