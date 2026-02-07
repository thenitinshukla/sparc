#!/usr/bin/env python3
"""
Plot Strong and Weak Scaling Results
Generates: Speedup, Efficiency, and Execution Time plots
Reads from results folders with timestamp
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from pathlib import Path

# Configuration
RESULTS_BASE = "results"
PLOTS_DIR = os.path.join(RESULTS_BASE, "plots")

# Create plots directory
os.makedirs(PLOTS_DIR, exist_ok=True)

def find_result_directories(scaling_type):
    """Find all result directories for a given scaling type."""
    pattern = os.path.join(RESULTS_BASE, f"{scaling_type}_scaling_*")
    dirs = glob.glob(pattern)
    # Sort by directory name (which includes timestamp)
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
            # Skip comments and empty lines
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
    # Extract pattern like 20260117_090937
    import re
    match = re.search(r'\d{8}_\d{6}', basename)
    return match.group(0) if match else ""

def select_directory(dirs, scaling_type):
    """Interactive directory selection."""
    if not dirs:
        print(f"No {scaling_type} scaling results found!")
        return None
    
    print(f"\nAvailable {scaling_type} scaling results:")
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
    """Generate strong scaling plots: speedup and efficiency."""
    if nodes is None or len(nodes) == 0:
        print("Skipping strong scaling plots - no data available")
        return
    
    # Calculate speedup and efficiency
    t_baseline = times[0]  # Time with smallest node count
    speedup = t_baseline / times
    ideal_speedup = nodes / nodes[0]
    efficiency = (speedup / (nodes / nodes[0])) * 100  # Percentage
    
    # Create figure with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    title_suffix = f" ({timestamp})" if timestamp else ""
    
    # Plot 1: Execution Time vs Nodes
    axes[0].plot(nodes, times, 'o-', linewidth=2, markersize=8, label='Actual Time')
    axes[0].set_xlabel('Number of Nodes', fontsize=12)
    axes[0].set_ylabel('Execution Time (s)', fontsize=12)
    axes[0].set_title(f'Strong Scaling: Execution Time{title_suffix}', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[0].set_xscale('log', base=2)
    
    # Plot 2: Speedup vs Nodes
    axes[1].plot(nodes, speedup, 'o-', linewidth=2, markersize=8, label='Actual Speedup')
    axes[1].plot(nodes, ideal_speedup, '--', linewidth=2, alpha=0.7, label='Ideal Speedup')
    axes[1].set_xlabel('Number of Nodes', fontsize=12)
    axes[1].set_ylabel('Speedup', fontsize=12)
    axes[1].set_title(f'Strong Scaling: Speedup{title_suffix}', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    axes[1].set_xscale('log', base=2)
    axes[1].set_yscale('log', base=2)
    
    # Plot 3: Efficiency vs Nodes
    axes[2].plot(nodes, efficiency, 'o-', linewidth=2, markersize=8, label='Parallel Efficiency')
    axes[2].axhline(y=100, color='r', linestyle='--', linewidth=2, alpha=0.7, label='Ideal (100%)')
    axes[2].set_xlabel('Number of Nodes', fontsize=12)
    axes[2].set_ylabel('Efficiency (%)', fontsize=12)
    axes[2].set_title(f'Strong Scaling: Efficiency{title_suffix}', fontsize=14, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()
    axes[2].set_xscale('log', base=2)
    axes[2].set_ylim(0, 110)
    
    plt.tight_layout()
    output_name = f'strong_scaling_{timestamp}.png' if timestamp else 'strong_scaling.png'
    output_file = os.path.join(PLOTS_DIR, output_name)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Strong scaling plot saved: {output_file}")
    
    # Print summary
    print("\nStrong Scaling Summary:")
    print(f"{'Nodes':<8} {'Time(s)':<12} {'Speedup':<10} {'Efficiency(%)':<15}")
    print("-" * 50)
    for i in range(len(nodes)):
        print(f"{nodes[i]:<8} {times[i]:<12.2f} {speedup[i]:<10.2f} {efficiency[i]:<15.2f}")

def plot_weak_scaling(nodes, times, timestamp=""):
    """Generate weak scaling plots: time and efficiency."""
    if nodes is None or len(nodes) == 0:
        print("Skipping weak scaling plots - no data available")
        return
    
    # Calculate efficiency (ideal is constant time)
    t_baseline = times[0]  # Time with smallest node count
    efficiency = (t_baseline / times) * 100  # Percentage
    
    # Create figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    title_suffix = f" ({timestamp})" if timestamp else ""
    
    # Plot 1: Execution Time vs Nodes
    axes[0].plot(nodes, times, 'o-', linewidth=2, markersize=8, label='Actual Time')
    axes[0].axhline(y=t_baseline, color='r', linestyle='--', linewidth=2, 
                    alpha=0.7, label=f'Ideal Time ({t_baseline:.2f}s)')
    axes[0].set_xlabel('Number of Nodes', fontsize=12)
    axes[0].set_ylabel('Execution Time (s)', fontsize=12)
    axes[0].set_title(f'Weak Scaling: Execution Time{title_suffix}', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[0].set_xscale('log', base=2)
    
    # Plot 2: Efficiency vs Nodes
    axes[1].plot(nodes, efficiency, 'o-', linewidth=2, markersize=8, label='Weak Scaling Efficiency')
    axes[1].axhline(y=100, color='r', linestyle='--', linewidth=2, alpha=0.7, label='Ideal (100%)')
    axes[1].set_xlabel('Number of Nodes', fontsize=12)
    axes[1].set_ylabel('Efficiency (%)', fontsize=12)
    axes[1].set_title(f'Weak Scaling: Efficiency{title_suffix}', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    axes[1].set_xscale('log', base=2)
    axes[1].set_ylim(0, 110)
    
    plt.tight_layout()
    output_name = f'weak_scaling_{timestamp}.png' if timestamp else 'weak_scaling.png'
    output_file = os.path.join(PLOTS_DIR, output_name)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Weak scaling plot saved: {output_file}")
    
    # Print summary
    print("\nWeak Scaling Summary:")
    print(f"{'Nodes':<8} {'Time(s)':<12} {'Efficiency(%)':<15}")
    print("-" * 40)
    for i in range(len(nodes)):
        print(f"{nodes[i]:<8} {times[i]:<12.2f} {efficiency[i]:<15.2f}")

def main():
    print("="*60)
    print("  Plotting Scaling Results")
    print("="*60)
    print()
    
    # Strong scaling
    strong_dirs = find_result_directories("strong")
    if strong_dirs:
        strong_dir = select_directory(strong_dirs, "Strong")
        if strong_dir:
            print(f"\nUsing: {os.path.basename(strong_dir)}")
            timestamp = extract_timestamp(strong_dir)
            nodes_strong, times_strong = load_data_from_dir(strong_dir)
            if nodes_strong is not None:
                plot_strong_scaling(nodes_strong, times_strong, timestamp)
                # Save plot to the same results directory
                plot_file = os.path.join(strong_dir, "strong_scaling_plot.png")
                import shutil
                src = os.path.join(PLOTS_DIR, f'strong_scaling_{timestamp}.png')
                if os.path.exists(src):
                    shutil.copy(src, plot_file)
                    print(f"✓ Plot also saved to: {plot_file}")
    print()
    
    # Weak scaling
    weak_dirs = find_result_directories("weak")
    if weak_dirs:
        weak_dir = select_directory(weak_dirs, "Weak")
        if weak_dir:
            print(f"\nUsing: {os.path.basename(weak_dir)}")
            timestamp = extract_timestamp(weak_dir)
            nodes_weak, times_weak = load_data_from_dir(weak_dir)
            if nodes_weak is not None:
                plot_weak_scaling(nodes_weak, times_weak, timestamp)
                # Save plot to the same results directory
                plot_file = os.path.join(weak_dir, "weak_scaling_plot.png")
                import shutil
                src = os.path.join(PLOTS_DIR, f'weak_scaling_{timestamp}.png')
                if os.path.exists(src):
                    shutil.copy(src, plot_file)
                    print(f"✓ Plot also saved to: {plot_file}")
    print()
    
    print("="*60)
    print(f"All plots saved in: {PLOTS_DIR}/")
    print("Plots also saved in respective result directories")
    print("="*60)

if __name__ == "__main__":
    main()
