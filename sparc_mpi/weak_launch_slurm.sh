#!/bin/bash

# ========================================================
# SPARC-MPI Slurm Launch Script (Leonardo DCGP)
# Weak Scaling Study
# ========================================================

# Configuration
NODE_MAX=16
TASKS_PER_NODE=112
PARTICLES_PER_NODE=50000 ##125000000  # 2M particles per node
                       
# Create timestamp for unique run directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BASE_DIR="slurm_runs/weak_scaling_${TIMESTAMP}"

TEMPLATE="run_slurm.sh"

# Node counts to test (powers of 2 for typical scaling studies)
NODES_LIST="1 2 4 8 16"

# Check if template file exists
if [ ! -f "$TEMPLATE" ]; then
    echo "Error: Template file '$TEMPLATE' not found!"
    exit 1
fi

echo "=========================================================="
echo "   SPARC-MPI Slurm Launch Script (Leonardo DCGP)"
echo "   Weak Scaling Study"
echo "   Run Directory: $BASE_DIR"
echo "   Timestamp: $TIMESTAMP"
echo "   Particles per node: $PARTICLES_PER_NODE"
echo "   Node counts: $NODES_LIST"
echo "   Tasks per node: $TASKS_PER_NODE"
echo "=========================================================="
echo ""

# Create base directory
mkdir -p "$BASE_DIR"

# Helper function to generate input file
generate_input() {
    local n=$1
    local nodes=$2
    local filename=$3
    cat > "$filename" << EOF
# Simulation Parameters - Weak Scaling
# Node count: ${nodes}
# Particles per node: ${PARTICLES_PER_NODE}
N = ${n}              # Total number of particles
R = 1.0               # Radius of the sphere
dt = 0.001            # Time step
tend = 1.0            # End time
SAVE_INTERVAL = 100   # Save data every N steps
MAX_SPECIES = 10      # Maximum number of particle species
BUFFER_SIZE = 32768   # Buffer size for file I/O

# Particle Species
species electron  1.0        # Species 1: electrons
species proton    1836.0     # Species 2: protons
EOF
}

# Create summary file
SUMMARY_FILE="${BASE_DIR}/weak_scaling_summary.txt"
echo "Weak Scaling Benchmark Summary" > "$SUMMARY_FILE"
echo "Generated: $(date)" >> "$SUMMARY_FILE"
echo "Particles per node: $PARTICLES_PER_NODE" >> "$SUMMARY_FILE"
echo "======================================" >> "$SUMMARY_FILE"
printf "%-10s %-15s %-15s %-10s\n" "Nodes" "Total_Particles" "Total_Tasks" "Job_ID" >> "$SUMMARY_FILE"
echo "--------------------------------------" >> "$SUMMARY_FILE"

# Loop over node counts
for NODES in $NODES_LIST; do
    # Skip if exceeds maximum
    if [ $NODES -gt $NODE_MAX ]; then
        echo "Skipping $NODES nodes (exceeds NODE_MAX=$NODE_MAX)"
        continue
    fi
    
    # Calculate total particles for weak scaling (scales with nodes)
    TOTAL_PARTICLES=$((NODES * PARTICLES_PER_NODE))
    
    # Create directory for this run
    RUN_DIR="${BASE_DIR}/node_${NODES}"
    mkdir -p "$RUN_DIR"
    
    echo "Preparing weak scaling run for $NODES nodes..."
    echo "  Directory: $RUN_DIR"
    echo "  Total particles: $TOTAL_PARTICLES (${PARTICLES_PER_NODE} per node)"
    
    # 1. Generate input file with scaled particle count
    generate_input $TOTAL_PARTICLES $NODES "${RUN_DIR}/input_file.txt"
    echo "  ✓ Created input_file.txt"
    
    # 2. Create job script from template
    TOTAL_TASKS=$((NODES * TASKS_PER_NODE))
    JOB_SCRIPT="${RUN_DIR}/job.sh"
    
    # Replace NODE_COUNT placeholder in template
    sed "s/NODE_COUNT/${NODES}/g" "$TEMPLATE" > "$JOB_SCRIPT"
    
    echo "  ✓ Created job.sh (nodes=$NODES, total_tasks=$TOTAL_TASKS)"
    
    # 3. Submit job
    CURRENT_DIR=$(pwd)
    cd "$RUN_DIR"
    
    echo "  Submitting job..."
    JOB_OUTPUT=$(sbatch job.sh 2>&1)
    JOB_ID=$(echo "$JOB_OUTPUT" | grep -oP '(?<=Submitted batch job )\d+')
    
    if [ -n "$JOB_ID" ]; then
        echo "  ✓ Job submitted: ID=$JOB_ID"
        # Add to summary
        printf "%-10s %-15s %-15s %-10s\n" "$NODES" "$TOTAL_PARTICLES" "$TOTAL_TASKS" "$JOB_ID" >> "$CURRENT_DIR/$SUMMARY_FILE"
    else
        echo "  ✗ Job submission failed: $JOB_OUTPUT"
        printf "%-10s %-15s %-15s %-10s\n" "$NODES" "$TOTAL_PARTICLES" "$TOTAL_TASKS" "FAILED" >> "$CURRENT_DIR/$SUMMARY_FILE"
    fi
    
    cd "$CURRENT_DIR"
    echo ""
done

echo "=========================================================="
echo "All weak scaling jobs submitted successfully!"
echo "Results will be in: $BASE_DIR"
echo ""
echo "Summary saved to: $SUMMARY_FILE"
echo ""
cat "$SUMMARY_FILE"
echo ""
echo "Monitor jobs with: squeue -u \$USER"
echo "=========================================================="
