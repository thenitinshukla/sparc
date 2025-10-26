#!/usr/bin/env python3
"""
Analyze SPARC Cluster Benchmark Results
Generates detailed analysis and visualizations from cluster benchmark data
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def load_results(results_dir):
    """Load all benchmark results from CSV files"""
    results = {}
    
    for csv_file in Path(results_dir).glob("*_results.csv"):
        impl_name = csv_file.stem.replace('_results', '')
        
        try:
            df = pd.read_csv(csv_file)
            results[impl_name] = df
            print(f"✓ Loaded: {impl_name} ({len(df)} measurements)")
        except Exception as e:
            print(f"✗ Error loading {csv_file}: {e}")
    
    return results

def calculate_statistics(results):
    """Calculate mean, std, min, max for each configuration"""
    stats = {}
    
    for impl_name, df in results.items():
        impl_stats = {}
        
        for n in df['N'].unique():
            n_data = df[df['N'] == n]['Time(s)']
            
            impl_stats[n] = {
                'mean': n_data.mean(),
                'std': n_data.std(),
                'min': n_data.min(),
                'max': n_data.max(),
                'count': len(n_data)
            }
        
        stats[impl_name] = impl_stats
    
    return stats

def plot_performance(results, stats, output_file):
    """Create comprehensive performance plots"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('SPARC Cluster Benchmark Results', fontsize=16, fontweight='bold')
    
    colors = {'python': '#2ecc71', 'serial': '#3498db', 'optimized': '#e74c3c',
              'fastmath': '#f39c12', 'parallel_omp': '#9b59b6', 'par_unseq': '#1abc9c'}
    
    # Plot 1: Execution time vs N
    for impl_name, impl_stats in stats.items():
        ns = sorted(impl_stats.keys())
        means = [impl_stats[n]['mean'] for n in ns]
        stds = [impl_stats[n]['std'] for n in ns]
        
        color = colors.get(impl_name, '#34495e')
        axes[0, 0].errorbar(ns, means, yerr=stds, label=impl_name,
                           color=color, marker='o', linewidth=2, markersize=8, capsize=5)
    
    axes[0, 0].set_xlabel('Number of Particles', fontweight='bold')
    axes[0, 0].set_ylabel('Execution Time (s)', fontweight='bold')
    axes[0, 0].set_title('Execution Time vs Problem Size', fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_xscale('log')
    axes[0, 0].set_yscale('log')
    
    # Plot 2: Speedup vs Serial
    if 'serial' in stats:
        serial_stats = stats['serial']
        
        for impl_name, impl_stats in stats.items():
            if impl_name == 'serial':
                continue
            
            ns = []
            speedups = []
            
            for n in sorted(impl_stats.keys()):
                if n in serial_stats:
                    speedup = serial_stats[n]['mean'] / impl_stats[n]['mean']
                    ns.append(n)
                    speedups.append(speedup)
            
            if ns:
                color = colors.get(impl_name, '#34495e')
                axes[0, 1].plot(ns, speedups, label=impl_name,
                               color=color, marker='o', linewidth=2, markersize=8)
        
        axes[0, 1].axhline(y=1, color='red', linestyle='--', alpha=0.5, label='Serial baseline')
        axes[0, 1].set_xlabel('Number of Particles', fontweight='bold')
        axes[0, 1].set_ylabel('Speedup vs Serial', fontweight='bold')
        axes[0, 1].set_title('Speedup Analysis', fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].set_xscale('log')
    
    # Plot 3: Scaling efficiency
    axes[1, 0].text(0.5, 0.5, 'Scaling Analysis', ha='center', va='center',
                    fontsize=14, fontweight='bold')
    axes[1, 0].axis('off')
    
    # Create table
    table_data = [['Implementation', 'N=1000', 'N=5000', 'N=10000', 'Speedup']]
    table_data.append(['─'*15, '─'*8, '─'*8, '─'*8, '─'*8])
    
    for impl_name in ['serial', 'optimized', 'parallel_omp', 'par_unseq']:
        if impl_name not in stats:
            continue
        
        row = [impl_name]
        for n in [1000, 5000, 10000]:
            if n in stats[impl_name]:
                row.append(f"{stats[impl_name][n]['mean']:.2f}s")
            else:
                row.append("N/A")
        
        # Speedup for N=10000
        if 'serial' in stats and 10000 in stats['serial'] and 10000 in stats[impl_name]:
            speedup = stats['serial'][10000]['mean'] / stats[impl_name][10000]['mean']
            row.append(f"{speedup:.2f}x")
        else:
            row.append("N/A")
        
        table_data.append(row)
    
    table = axes[1, 0].table(cellText=table_data, cellLoc='center',
                            loc='center', colWidths=[0.25, 0.15, 0.15, 0.15, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    for i in range(len(table_data[0])):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Plot 4: Box plot for largest N
    max_n = max([max(impl_stats.keys()) for impl_stats in stats.values()])
    box_data = []
    box_labels = []
    
    for impl_name, df in results.items():
        if max_n in df['N'].values:
            n_data = df[df['N'] == max_n]['Time(s)'].values
            box_data.append(n_data)
            box_labels.append(impl_name)
    
    if box_data:
        bp = axes[1, 1].boxplot(box_data, labels=box_labels, patch_artist=True)
        
        for patch, label in zip(bp['boxes'], box_labels):
            patch.set_facecolor(colors.get(label, '#34495e'))
        
        axes[1, 1].set_ylabel('Execution Time (s)', fontweight='bold')
        axes[1, 1].set_title(f'Distribution for N={max_n}', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Plot saved to: {output_file}")

def print_detailed_report(stats):
    """Print detailed statistical report"""
    
    print("\n" + "="*80)
    print("DETAILED PERFORMANCE REPORT")
    print("="*80)
    print()
    
    for impl_name, impl_stats in sorted(stats.items()):
        print(f"\n{impl_name.upper()}")
        print("-"*80)
        print(f"{'N':<10} {'Mean (s)':<12} {'Std (s)':<12} {'Min (s)':<12} {'Max (s)':<12}")
        print("-"*80)
        
        for n in sorted(impl_stats.keys()):
            s = impl_stats[n]
            print(f"{n:<10} {s['mean']:<12.4f} {s['std']:<12.4f} {s['min']:<12.4f} {s['max']:<12.4f}")
    
    # Speedup analysis
    if 'serial' in stats:
        print("\n" + "="*80)
        print("SPEEDUP ANALYSIS (vs Serial)")
        print("="*80)
        print()
        print(f"{'Implementation':<20}", end='')
        
        all_ns = sorted(set([n for impl_stats in stats.values() for n in impl_stats.keys()]))
        for n in all_ns:
            print(f"N={n:<8}", end=' ')
        print()
        print("-"*80)
        
        serial_stats = stats['serial']
        for impl_name, impl_stats in sorted(stats.items()):
            if impl_name == 'serial':
                continue
            
            print(f"{impl_name:<20}", end='')
            for n in all_ns:
                if n in impl_stats and n in serial_stats:
                    speedup = serial_stats[n]['mean'] / impl_stats[n]['mean']
                    print(f"{speedup:>6.2f}x    ", end='')
                else:
                    print(f"{'N/A':<11}", end='')
            print()


if __name__ == "__main__":
    main()
