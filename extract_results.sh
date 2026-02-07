#!/bin/bash

# ========================================================
# Extract Execution Times from SLURM Job Outputs
# Creates a single results file per run with timestamp
# ========================================================

SLURM_BASE="slurm_runs"
RESULTS_BASE="results"

echo "=========================================================="
echo "  Extracting Execution Times from SLURM Jobs"
echo "=========================================================="
echo ""

# Function to extract results from a specific run directory
extract_run() {
    local run_dir=$1
    local run_name=$(basename "$run_dir")
    
    # Extract timestamp from directory name
    # e.g., strong_scaling_20260117_090937 -> 20260117_090937
    local timestamp=$(echo "$run_name" | grep -oP '\d{8}_\d{6}')
    
    if [ -z "$timestamp" ]; then
        echo "  Warning: Could not extract timestamp from $run_name"
        return
    fi
    
    # Determine scaling type
    local scaling_type=""
    if [[ "$run_name" == strong_scaling_* ]]; then
        scaling_type="strong"
    elif [[ "$run_name" == weak_scaling_* ]]; then
        scaling_type="weak"
    else
        echo "  Warning: Unknown scaling type for $run_name"
        return
    fi
    
    echo "Processing: $run_name"
    echo "  Timestamp: $timestamp"
    echo "  Type: ${scaling_type} scaling"
    
    # Create results directory for this run
    RESULTS_DIR="${RESULTS_BASE}/${scaling_type}_scaling_${timestamp}"
    mkdir -p "$RESULTS_DIR"
    
    # Output file
    OUTPUT_FILE="${RESULTS_DIR}/results.txt"
    
    # Create header
    echo "# ${scaling_type^} Scaling Results" > "$OUTPUT_FILE"
    echo "# Run timestamp: $timestamp" >> "$OUTPUT_FILE"
    echo "# Directory: $run_dir" >> "$OUTPUT_FILE"
    echo "# " >> "$OUTPUT_FILE"
    echo "# Nodes  ExecutionTime(s)" >> "$OUTPUT_FILE"
    
    # Loop through node directories
    for node_dir in $(ls -d "$run_dir"/node_* 2>/dev/null | sort -V); do
        if [ ! -d "$node_dir" ]; then
            continue
        fi
        
        # Extract node count from directory name
        nodes=$(basename "$node_dir" | sed 's/node_//')
        
        # Find the job output file
        job_out=$(ls -t "$node_dir"/job.out.* 2>/dev/null | head -1)
        
        if [ -z "$job_out" ]; then
            echo "    Warning: No job output in node_${nodes}"
            continue
        fi
        
        # Extract execution time - looking for "Total execution time: XX.XXX seconds"
        exec_time=$(grep -i "Total execution time:" "$job_out" | grep -oP '\d+\.\d+' | head -1)
        
        if [ -z "$exec_time" ]; then
            echo "    Warning: No execution time found for node_${nodes}"
            continue
        fi
        
        # Append to output file
        printf "%-8s %.3f\n" "$nodes" "$exec_time" >> "$OUTPUT_FILE"
        echo "    ✓ node_${nodes}: ${exec_time}s"
    done
    
    echo "  Results saved to: $OUTPUT_FILE"
    echo ""
    
    # Display the results
    echo "  ----------------------------------------"
    cat "$OUTPUT_FILE"
    echo "  ----------------------------------------"
    echo ""
}

# Find all scaling run directories
echo "Searching for scaling runs in: $SLURM_BASE"
echo ""

# Process strong scaling runs
strong_runs=$(ls -dt "$SLURM_BASE"/strong_scaling_* 2>/dev/null)
if [ -n "$strong_runs" ]; then
    echo "Found Strong Scaling Runs:"
    for run in $strong_runs; do
        echo "  - $(basename $run)"
    done
    echo ""
    
    for run in $strong_runs; do
        extract_run "$run"
    done
fi

# Process weak scaling runs
weak_runs=$(ls -dt "$SLURM_BASE"/weak_scaling_* 2>/dev/null)
if [ -n "$weak_runs" ]; then
    echo "Found Weak Scaling Runs:"
    for run in $weak_runs; do
        echo "  - $(basename $run)"
    done
    echo ""
    
    for run in $weak_runs; do
        extract_run "$run"
    done
fi

echo "=========================================================="
echo "Extraction complete!"
echo ""
echo "Results organized in: $RESULTS_BASE/"
echo ""
echo "Directory structure:"
ls -R "$RESULTS_BASE" 2>/dev/null
echo ""
echo "Next: Run plot_scaling_results.py to generate plots"
echo "=========================================================="
