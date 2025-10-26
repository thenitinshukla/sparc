#!/usr/bin/env python3
"""
SPARC Benchmark Visualization
Creates plots comparing all implementations
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys

def load_latest_benchmark(results_dir="results"):
    """Load the most recent benchmark results"""
    results_path = Path(results_dir)
    
    if not results_path.exists():
        print(f"Results directory '{results_dir}' not found")
        return None
    
    json_files = sorted(results_path.glob("benchmark_*.json"))
    
    if not json_files:
        print("No benchmark results found")
        return None
    
    latest = json_files[-1]
    print(f"Loading: {latest}")
    
    with open(latest, 'r') as f:
        return json.load(f)


def plot_performance_comparison(results):
    """Create performance comparison plots"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('SPARC Implementation Benchmark Comparison', fontsize=16, fontweight='bold')
    
    # Extract data
    names = []
    times = []
    energies_initial = []
    energies_final = []
    drifts = []
    
    for name, data in sorted(results.items()):
        names.append(name)
        times.append(data['elapsed_time'])
        energies_initial.append(data['energy_data']['initial_energy'])
        energies_final.append(data['energy_data']['final_energy'])
        drifts.append(abs(data['energy_data']['energy_drift']))
    
    # 1. Execution Time
    colors = ['#2ecc71' if n == 'python' else '#3498db' for n in names]
    axes[0, 0].bar(range(len(names)), times, color=colors, edgecolor='black', linewidth=1.5)
    axes[0, 0].set_xticks(range(len(names)))
    axes[0, 0].set_xticklabels(names, rotation=45, ha='right')
    axes[0, 0].set_ylabel('Time (seconds)', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Execution Time', fontsize=12, fontweight='bold')
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, (t, n) in enumerate(zip(times, names)):
        axes[0, 0].text(i, t, f'{t:.2f}s', ha='center', va='bottom', fontweight='bold')
    
    # 2. Speedup relative to Python
    if 'python' in results:
        ref_time = results['python']['elapsed_time']
        speedups = [ref_time / t for t in times]
        
        colors_speedup = ['#e74c3c' if s < 1 else '#27ae60' for s in speedups]
        axes[0, 1].bar(range(len(names)), speedups, color=colors_speedup, edgecolor='black', linewidth=1.5)
        axes[0, 1].axhline(y=1, color='red', linestyle='--', linewidth=2, label='Python baseline')
        axes[0, 1].set_xticks(range(len(names)))
        axes[0, 1].set_xticklabels(names, rotation=45, ha='right')
        axes[0, 1].set_ylabel('Speedup Factor', fontsize=11, fontweight='bold')
        axes[0, 1].set_title('Speedup vs Python', fontsize=12, fontweight='bold')
        axes[0, 1].grid(axis='y', alpha=0.3)
        axes[0, 1].legend()
        
        # Add value labels
        for i, s in enumerate(speedups):
            axes[0, 1].text(i, s, f'{s:.2f}x', ha='center', va='bottom', fontweight='bold')
    
    # 3. Energy Drift
    colors_drift = ['#e74c3c' if d > 0.1 else '#27ae60' for d in drifts]
    axes[0, 2].bar(range(len(names)), drifts, color=colors_drift, edgecolor='black', linewidth=1.5)
    axes[0, 2].axhline(y=0.1, color='orange', linestyle='--', linewidth=2, label='0.1% threshold')
    axes[0, 2].set_xticks(range(len(names)))
    axes[0, 2].set_xticklabels(names, rotation=45, ha='right')
    axes[0, 2].set_ylabel('Energy Drift (%)', fontsize=11, fontweight='bold')
    axes[0, 2].set_title('Energy Conservation', fontsize=12, fontweight='bold')
    axes[0, 2].grid(axis='y', alpha=0.3)
    axes[0, 2].legend()
    
    # 4. Energy Evolution Over Time
    for name, data in sorted(results.items()):
        time_arr = data['energy_data']['time']
        energy_arr = data['energy_data']['energy']
        axes[1, 0].plot(time_arr, energy_arr, marker='o', label=name, linewidth=2, markersize=4)
    
    axes[1, 0].set_xlabel('Time (s)', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Total Energy', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Energy Evolution', fontsize=12, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 5. Normalized Energy Evolution
    for name, data in sorted(results.items()):
        time_arr = data['energy_data']['time']
        energy_arr = data['energy_data']['energy']
        E0 = energy_arr[0]
        normalized = [(e - E0) / E0 * 100 for e in energy_arr]
        axes[1, 1].plot(time_arr, normalized, marker='o', label=name, linewidth=2, markersize=4)
    
    axes[1, 1].axhline(y=0, color='black', linestyle=':', alpha=0.5)
    axes[1, 1].set_xlabel('Time (s)', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('(E - E₀) / E₀ (%)', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Normalized Energy Evolution', fontsize=12, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    # 6. Accuracy Comparison Table
    axes[1, 2].axis('off')
    
    if 'python' in results:
        ref_energy = results['python']['energy_data']['initial_energy']
        
        table_data = []
        table_data.append(['Implementation', 'Energy Diff %', 'Status'])
        table_data.append(['─' * 15, '─' * 12, '─' * 10])
        
        for name, data in sorted(results.items()):
            if name == 'python':
                continue
            energy = data['energy_data']['initial_energy']
            diff = abs(energy - ref_energy) / ref_energy * 100
            status = '✓ PASS' if diff < 1.0 else '⚠ WARN'
            table_data.append([name, f'{diff:.4f}%', status])
        
        table = axes[1, 2].table(cellText=table_data, cellLoc='left',
                                  loc='center', colWidths=[0.4, 0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Style header
        for i in range(3):
            table[(0, i)].set_facecolor('#3498db')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        axes[1, 2].set_title('Accuracy Comparison\n(vs Python Reference)', 
                            fontsize=12, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    # Save figure
    output_file = 'benchmark_comparison.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Visualization saved to: {output_file}")
    
    plt.show()


def print_detailed_report(results):
    """Print detailed text report"""
    print("\n" + "="*80)
    print("DETAILED BENCHMARK REPORT")
    print("="*80)
    
    for name, data in sorted(results.items()):
        print(f"\n{name.upper()}")
        print("-" * 80)
        print(f"  Execution Time:     {data['elapsed_time']:.3f} seconds")
        print(f"  Initial Energy:     {data['energy_data']['initial_energy']:.6e}")
        print(f"  Final Energy:       {data['energy_data']['final_energy']:.6e}")
        print(f"  Energy Drift:       {data['energy_data']['energy_drift']:.6f}%")
        
        if 'num_particles' in data['energy_data']:
            print(f"  Particles:          {data['energy_data']['num_particles']}")
        
        print(f"  Timestamp:          {data['timestamp']}")
    
    print("\n" + "="*80)


def main():
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    else:
        results_dir = "results"
    
    results = load_latest_benchmark(results_dir)
    
    if results is None:
        print("No results to visualize")
        return
    
    print_detailed_report(results)
    plot_performance_comparison(results)


if __name__ == "__main__":
    main()
