#!/usr/bin/env python3
"""
Plot Strong Scaling Results
Generates: Speedup and Efficiency plots with dual y-axes
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import re

# Configuration
RESULTS_BASE = "results"
PLOTS_DIR = os.path.join(RESULTS_BASE, "plots")

# Create plots directory
os.makedirs(PLOTS_DIR, exist_ok=True)

def find_result_directories():
    """Find all strong scaling result directories."""
    pattern = os.path.join(RESULTS_BASE, "strong_scaling_*")
    dirs = glob.glob(pattern)
    dirs.sort(reverse=True)
    return dirs

def load_data_from_dir(result_dir):
    """Load timing data from results.txt in a directory."""
    results_file = os.path.join(result_dir, "results.txt")
    
    if not os.path.exists(results_file):
        print(f"Warning: {results_file} not found!")
        return None, None
    
    nodes = []
    times = []
    
    with open(results_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            
            parts = line.split()
            if len(parts) >= 2:
                try:
                    nodes.append(int(parts[0]))
                    times.append(float(parts[1]))
                except ValueError:
                    continue
    
    if not nodes:
        print(f"Warning: No data found in {results_file}")
        return None, None
    
    return np.array(nodes), np.array(times)

def extract_timestamp(dirname):
    """Extract timestamp from directory name."""
    basename = os.path.basename(dirname)
    match = re.search(r'\d{8}_\d{6}', basename)
    return match.group(0) if match else ""

def select_directory(dirs):
    """Interactive directory selection."""
    if not dirs:
        print("No strong scaling results found!")
        return None
    
    print("\nAvailable strong scaling results:")
    print("  0) Most recent:", os.path.basename(dirs[0]))
    
    for i, d in enumerate(dirs, 1):
        print(f"  {i}) {os.path.basename(d)}")
    
    choice = input(f"\nSelect result (0-{len(dirs)}, or Enter for most recent): ").strip()
    
    if not choice or choice == "0":
        return dirs[0]
    
    try:
        idx = int(choice)
        if 1 <= idx <= len(dirs):
            return dirs[idx - 1]
    except ValueError:
        pass
    
    return dirs[0]

def plot_strong_scaling(nodes, times, timestamp=""):
    """Generate strong scaling plot with dual y-axes."""
    if nodes is None or len(nodes) == 0:
        print("No data available for plotting")
        return
    
    # Calculate speedup and efficiency
    t_baseline = times[0]
    speedup = t_baseline / times
    ideal_speedup = nodes / nodes[0]
    efficiency = (speedup / (nodes / nodes[0])) * 100
    
    # Main plot: Dual y-axes (reference style)
    fig, ax1 = plt.subplots(figsize=(12, 7))
    
    # Left y-axis: Speedup
    color_speedup = '#1f77b4'  # Blue
    ax1.set_xlabel('Nodes', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Speedup', fontsize=14, fontweight='bold')
    
    # Plot speedup (solid line)
    line1 = ax1.plot(nodes, speedup, 'o-', linewidth=2.5, markersize=10, 
                     color=color_speedup, label='Speedup')
    # Plot ideal speedup (black solid line)
    line2 = ax1.plot(nodes, ideal_speedup, 's-', linewidth=2.5, markersize=8,
                     color='black', label='Ideal Speedup')
    
    ax1.set_xscale('log', base=2)
    ax1.set_yscale('log', base=10)
    ax1.tick_params(axis='y', labelcolor=color_speedup, labelsize=12)
    ax1.tick_params(axis='x', labelsize=12)
    ax1.grid(True, alpha=0.3, which='both')
    
    # Right y-axis: Efficiency
    ax2 = ax1.twinx()
    color_efficiency = '#ff7f0e'  # Orange
    ax2.set_ylabel('Efficiency', fontsize=14, fontweight='bold')
    
    # Plot efficiency (dashed line)
    line3 = ax2.plot(nodes, efficiency, 'o--', linewidth=2.5, markersize=10,
                     color=color_efficiency, label='Efficiency')
    # Plot ideal efficiency (dashed line at 100%)
    ideal_efficiency = np.ones_like(nodes) * 100
    line4 = ax2.plot(nodes, ideal_efficiency, 's--', linewidth=2.5, markersize=8,
                     color='black', alpha=0.7, label='Ideal Efficiency')
    
    ax2.tick_params(axis='y', labelcolor=color_efficiency, labelsize=12)
    ax2.set_ylim(0, 110)
    
    # Set x-axis ticks
    ax1.set_xticks(nodes)
    ax1.set_xticklabels([str(n) for n in nodes])
    
    # Combine legends
    lines = line1 + line2 + line3 + line4
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='best', fontsize=11, framealpha=0.9)
    
    title_suffix = f" ({timestamp})" if timestamp else ""
    plt.title(f'Strong Scaling Analysis{title_suffix}', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_name = f'strong_scaling_{timestamp}.png' if timestamp else 'strong_scaling.png'
    output_file = os.path.join(PLOTS_DIR, output_name)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Strong scaling plot saved: {output_file}")
    plt.close()
    
    # Detailed subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Plot 1: Execution Time vs Nodes
    axes[0].plot(nodes, times, 'o-', linewidth=2, markersize=8, label='Actual Time', color='#2ca02c')
    axes[0].set_xlabel('Number of Nodes', fontsize=12)
    axes[0].set_ylabel('Execution Time (s)', fontsize=12)
    axes[0].set_title('Execution Time vs Nodes', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[0].set_xscale('log', base=2)
    axes[0].set_xticks(nodes)
    axes[0].set_xticklabels([str(n) for n in nodes])
    
    # Plot 2: Speedup vs Nodes
    axes[1].plot(nodes, speedup, 'o-', linewidth=2, markersize=8, label='Actual Speedup', color=color_speedup)
    axes[1].plot(nodes, ideal_speedup, 's--', linewidth=2, markersize=6, alpha=0.7, label='Ideal Speedup', color='black')
    axes[1].set_xlabel('Number of Nodes', fontsize=12)
    axes[1].set_ylabel('Speedup', fontsize=12)
    axes[1].set_title('Speedup vs Nodes', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    axes[1].set_xscale('log', base=2)
    axes[1].set_yscale('log', base=2)
    axes[1].set_xticks(nodes)
    axes[1].set_xticklabels([str(n) for n in nodes])
    
    # Plot 3: Efficiency vs Nodes
    axes[2].plot(nodes, efficiency, 'o-', linewidth=2, markersize=8, label='Parallel Efficiency', color=color_efficiency)
    axes[2].axhline(y=100, color='black', linestyle='--', linewidth=2, alpha=0.7, label='Ideal (100%)')
    axes[2].set_xlabel('Number of Nodes', fontsize=12)
    axes[2].set_ylabel('Efficiency (%)', fontsize=12)
    axes[2].set_title('Efficiency vs Nodes', fontsize=14, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()
    axes[2].set_xscale('log', base=2)
    axes[2].set_ylim(0, 110)
    axes[2].set_xticks(nodes)
    axes[2].set_xticklabels([str(n) for n in nodes])
    
    plt.tight_layout()
    output_name_detailed = f'strong_scaling_{timestamp}_detailed.png' if timestamp else 'strong_scaling_detailed.png'
    output_file_detailed = os.path.join(PLOTS_DIR, output_name_detailed)
    plt.savefig(output_file_detailed, dpi=300, bbox_inches='tight')
    print(f"✓ Detailed plots saved: {output_file_detailed}")
    plt.close()
    
    # Print summary
    print("\n" + "="*60)
    print("Strong Scaling Summary")
    print("="*60)
    print(f"{'Nodes':<8} {'Time(s)':<12} {'Speedup':<10} {'Efficiency(%)':<15}")
    print("-" * 60)
    for i in range(len(nodes)):
        print(f"{nodes[i]:<8} {times[i]:<12.3f} {speedup[i]:<10.2f} {efficiency[i]:<15.2f}")
    print("="*60)

def main():
    print("="*60)
    print("  Strong Scaling Results Plotter")
    print("="*60)
    
    dirs = find_result_directories()
    if not dirs:
        print("\nNo strong scaling results found!")
        print("Run extract_results.sh first to extract data from SLURM outputs.")
        return
    
    result_dir = select_directory(dirs)
    if not result_dir:
        return
    
    print(f"\nUsing: {os.path.basename(result_dir)}")
    timestamp = extract_timestamp(result_dir)
    
    nodes, times = load_data_from_dir(result_dir)
    if nodes is not None:
        plot_strong_scaling(nodes, times, timestamp)
        
        # Copy plots to result directory
        import shutil
        plot_file = os.path.join(result_dir, "strong_scaling_plot.png")
        plot_detailed_file = os.path.join(result_dir, "strong_scaling_detailed.png")
        
        src = os.path.join(PLOTS_DIR, f'strong_scaling_{timestamp}.png')
        src_detailed = os.path.join(PLOTS_DIR, f'strong_scaling_{timestamp}_detailed.png')
        
        if os.path.exists(src):
            shutil.copy(src, plot_file)
            print(f"✓ Main plot also saved to: {plot_file}")
        if os.path.exists(src_detailed):
            shutil.copy(src_detailed, plot_detailed_file)
            print(f"✓ Detailed plots also saved to: {plot_detailed_file}")
    
    print("\n" + "="*60)
    print(f"All plots saved in: {PLOTS_DIR}/")
    print("="*60)

if __name__ == "__main__":
    main()
