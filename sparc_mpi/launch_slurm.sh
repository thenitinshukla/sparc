#!/bin/bash

# ========================================================
# SPARC-MPI Slurm Launch Script (Leonardo DCGP)
# Strong Scaling Study
# ========================================================

# Configuration
NODE_MAX=32
TASKS_PER_NODE=112
STRONG_N=1200000000   ##1000000000  # 100 million particles (increased from 10M)
        
# Create timestamp for unique run directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BASE_DIR="slurm_runs/strong_scaling_${TIMESTAMP}"

TEMPLATE="run_slurm.sh"
INPUT_TEMPLATE="input_file.txt"

# Node counts to test (powers of 2 for comprehensive scaling studies)
NODES_LIST="8 16 32"

# Check if template files exist
if [ ! -f "$TEMPLATE" ]; then
    echo "Error: Template file '$TEMPLATE' not found!"
    exit 1
fi

if [ ! -f "$INPUT_TEMPLATE" ]; then
    echo "Error: Input template file '$INPUT_TEMPLATE' not found!"
    exit 1
fi

echo "=========================================================="
echo "   SPARC-MPI Slurm Launch Script (Leonardo DCGP)"
echo "   Strong Scaling Study: N=$STRONG_N"
echo "   Run Directory: $BASE_DIR"
echo "   Timestamp: $TIMESTAMP"
echo "   Node counts: $NODES_LIST"
echo "   Tasks per node: $TASKS_PER_NODE"
echo "=========================================================="
echo ""

# Create base directory
mkdir -p "$BASE_DIR"

# Helper function to generate input file
generate_input() {
    local n=$1
    local filename=$2
    cat > "$filename" << EOF
# Simulation Parameters
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

# Loop over node counts
for NODES in $NODES_LIST; do
    # Skip if exceeds maximum
    if [ $NODES -gt $NODE_MAX ]; then
        echo "Skipping $NODES nodes (exceeds NODE_MAX=$NODE_MAX)"
        continue
    fi
    
    # Create directory for this run
    RUN_DIR="${BASE_DIR}/node_${NODES}"
    mkdir -p "$RUN_DIR"
    
    echo "Preparing run for $NODES nodes..."
    echo "  Directory: $RUN_DIR"
    
    # 1. Generate input file with strong scaling particle count
    generate_input $STRONG_N "${RUN_DIR}/input_file.txt"
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
    JOB_ID=$(sbatch job.sh 2>&1 | grep -oP '(?<=Submitted batch job )\d+')
    
    if [ -n "$JOB_ID" ]; then
        echo "  ✓ Job submitted: ID=$JOB_ID"
    else
        echo "  ✗ Job submission failed"
    fi
    
    cd "$CURRENT_DIR"
    echo ""
done

echo "=========================================================="
echo "All jobs submitted successfully!"
echo "Results will be in: $BASE_DIR"
echo ""
echo "Monitor jobs with: squeue -u \$USER"
echo "=========================================================="
