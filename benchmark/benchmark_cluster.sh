#!/bin/bash
################################################################################
# SPARC Cluster Benchmark Script
# Designed for HPC cluster execution with SLURM/PBS
# 
# Usage:
#   sbatch benchmark_cluster.sh                    # SLURM
#   qsub benchmark_cluster.sh                      # PBS
#   ./benchmark_cluster.sh                         # Direct execution
################################################################################

#SBATCH --job-name=sparc_benchmark
#SBATCH --output=sparc_benchmark_%j.out
#SBATCH --error=sparc_benchmark_%j.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --partition=compute

#PBS -N sparc_benchmark
#PBS -l walltime=04:00:00
#PBS -l nodes=1:ppn=16
#PBS -l mem=32gb
#PBS -j oe

set -e

################################################################################
# Configuration
################################################################################

# Detect job scheduler
if [ ! -z "$SLURM_JOB_ID" ]; then
    SCHEDULER="SLURM"
    JOB_ID=$SLURM_JOB_ID
    NUM_THREADS=$SLURM_CPUS_PER_TASK
elif [ ! -z "$PBS_JOBID" ]; then
    SCHEDULER="PBS"
    JOB_ID=$PBS_JOBID
    NUM_THREADS=$(cat $PBS_NODEFILE | wc -l)
else
    SCHEDULER="DIRECT"
    JOB_ID=$$
    NUM_THREADS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
fi

# Set OMP threads
export OMP_NUM_THREADS=$NUM_THREADS

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║         SPARC Cluster Benchmark Suite                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo
echo "Scheduler: $SCHEDULER"
echo "Job ID: $JOB_ID"
echo "Threads: $NUM_THREADS"
echo "Node: $(hostname)"
echo "Date: $(date)"
echo

################################################################################
# Load modules (adjust for your cluster)
################################################################################

load_modules() {
    echo "Loading environment modules..."
    
    # Try to load common HPC modules
    if command -v module &> /dev/null; then
        # GCC compiler
        module load gcc/11.2.0 2>/dev/null || module load gcc 2>/dev/null || true
        
        # Intel TBB for par_unseq
        module load tbb 2>/dev/null || module load intel-tbb 2>/dev/null || true
        
        # Python
        module load python/3.9 2>/dev/null || module load python3 2>/dev/null || true
        
        # Intel Advisor (optional)
        module load advisor 2>/dev/null || true
        
        echo "✓ Modules loaded"
        module list 2>&1 | head -10
    else
        echo "  Module system not available, using environment defaults"
    fi
    echo
}

load_modules

################################################################################
# Result directory
################################################################################

RESULT_DIR="cluster_results_${JOB_ID}"
mkdir -p "$RESULT_DIR"

echo "Results will be saved to: $RESULT_DIR"
echo

################################################################################
# System information
################################################################################

collect_system_info() {
    local INFO_FILE="$RESULT_DIR/system_info.txt"
    
    {
        echo "╔════════════════════════════════════════════════════════════════════════╗"
        echo "║         System Information                                              ║"
        echo "╚════════════════════════════════════════════════════════════════════════╝"
        echo
        echo "Date: $(date)"
        echo "Hostname: $(hostname)"
        echo "Scheduler: $SCHEDULER"
        echo "Job ID: $JOB_ID"
        echo
        echo "CPU Information:"
        lscpu 2>/dev/null || sysctl -a | grep cpu 2>/dev/null || echo "  CPU info not available"
        echo
        echo "Memory Information:"
        free -h 2>/dev/null || vm_stat 2>/dev/null || echo "  Memory info not available"
        echo
        echo "Compiler Information:"
        gcc --version 2>/dev/null | head -1 || echo "  GCC not available"
        g++ --version 2>/dev/null | head -1 || echo "  G++ not available"
        echo
        echo "Python Information:"
        python --version 2>/dev/null || python3 --version 2>/dev/null || echo "  Python not available"
        echo
        echo "Environment Variables:"
        echo "  OMP_NUM_THREADS=$OMP_NUM_THREADS"
        echo "  PATH=$PATH"
        echo
    } > "$INFO_FILE"
    
    echo "✓ System information saved to: $INFO_FILE"
}

collect_system_info

################################################################################
# Benchmark configurations
################################################################################

# Test different particle counts
PARTICLE_COUNTS=(100 500 1000 5000 10000)

# Number of repetitions for timing accuracy
REPETITIONS=3

################################################################################
# Function to run a single benchmark
################################################################################

run_benchmark() {
    local NAME=$1
    local EXEC=$2
    local N=$3
    local REP=$4
    
    local INPUT_FILE="${RESULT_DIR}/input_N${N}.txt"
    local OUTPUT_FILE="${RESULT_DIR}/${NAME}_N${N}_rep${REP}.txt"
    
    # Create input file
    cat > "$INPUT_FILE" <<EOF
N = $N
R = 1.0
dt = 0.001
tend = 0.1
SAVE_INTERVAL = 10
species electron  1.0
EOF
    
    # Run benchmark and time it
    local START=$(date +%s.%N)
    
    if [ "$NAME" == "python" ]; then
        timeout 600 python "$EXEC" > "$OUTPUT_FILE" 2>&1
    else
        timeout 600 "$EXEC" "$INPUT_FILE" -n > "$OUTPUT_FILE" 2>&1
    fi
    
    local END=$(date +%s.%N)
    local ELAPSED=$(echo "$END - $START" | bc)
    
    # Extract energy conservation error
    local ENERGY_ERROR="N/A"
    if grep -q "energy conservation error" "$OUTPUT_FILE" 2>/dev/null; then
        ENERGY_ERROR=$(grep "energy conservation error" "$OUTPUT_FILE" | tail -1 | awk '{print $(NF-1)}')
    fi
    
    echo "$ELAPSED,$ENERGY_ERROR"
}

################################################################################
# Benchmark all implementations
################################################################################

benchmark_implementation() {
    local NAME=$1
    local EXEC=$2
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Benchmarking: $NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    if [ ! -f "$EXEC" ] && [ "$NAME" != "python" ]; then
        echo "  ✗ Executable not found: $EXEC"
        echo "  Skipping..."
        echo
        return
    fi
    
    local RESULTS_FILE="${RESULT_DIR}/${NAME}_results.csv"
    echo "N,Rep,Time(s),EnergyError(%)" > "$RESULTS_FILE"
    
    for N in "${PARTICLE_COUNTS[@]}"; do
        echo "  N=$N particles:"
        
        for ((rep=1; rep<=REPETITIONS; rep++)); do
            echo -n "    Repetition $rep/$REPETITIONS..."
            
            RESULT=$(run_benchmark "$NAME" "$EXEC" "$N" "$rep")
            TIME=$(echo "$RESULT" | cut -d',' -f1)
            ERROR=$(echo "$RESULT" | cut -d',' -f2)
            
            echo "$N,$rep,$TIME,$ERROR" >> "$RESULTS_FILE"
            echo " ${TIME}s (error: ${ERROR})"
        done
        echo
    done
    
    echo "✓ Results saved to: $RESULTS_FILE"
    echo
}

################################################################################
# Run benchmarks
################################################################################

echo "═══════════════════════════════════════════════════════════════════════════"
echo "Starting Benchmark Suite"
echo "═══════════════════════════════════════════════════════════════════════════"
echo

# Python reference
if [ -f "pythonsparc/main.py" ]; then
    # Modify Python script to use our input files
    benchmark_implementation "python" "pythonsparc/main.py"
fi

# Serial
if [ -f "bin/sparc_serial" ] || [ -f "bin/sparc_serial.exe" ]; then
    EXEC="bin/sparc_serial"
    [ -f "bin/sparc_serial.exe" ] && EXEC="bin/sparc_serial.exe"
    benchmark_implementation "serial" "$EXEC"
fi

# Optimized
if [ -f "bin/sparc_optimized" ] || [ -f "bin/sparc_optimized.exe" ]; then
    EXEC="bin/sparc_optimized"
    [ -f "bin/sparc_optimized.exe" ] && EXEC="bin/sparc_optimized.exe"
    benchmark_implementation "optimized" "$EXEC"
fi

# FastMath
if [ -f "bin/sparc_fastmath" ] || [ -f "bin/sparc_fastmath.exe" ]; then
    EXEC="bin/sparc_fastmath"
    [ -f "bin/sparc_fastmath.exe" ] && EXEC="bin/sparc_fastmath.exe"
    benchmark_implementation "fastmath" "$EXEC"
fi

# Parallel (OpenMP)
if [ -f "bin/sparc_parallel" ] || [ -f "bin/sparc_parallel.exe" ]; then
    EXEC="bin/sparc_parallel"
    [ -f "bin/sparc_parallel.exe" ] && EXEC="bin/sparc_parallel.exe"
    benchmark_implementation "parallel_omp" "$EXEC"
fi

# Par_Unseq
if [ -f "sparc_parunseq/bin/sparc_parunseq" ] || [ -f "sparc_parunseq/bin/sparc_parunseq.exe" ]; then
    EXEC="sparc_parunseq/bin/sparc_parunseq"
    [ -f "sparc_parunseq/bin/sparc_parunseq.exe" ] && EXEC="sparc_parunseq/bin/sparc_parunseq.exe"
    
    # Need to adjust path for input file
    cd sparc_parunseq
    benchmark_implementation "par_unseq" "../$EXEC"
    cd ..
fi

################################################################################
# Generate summary report
################################################################################

generate_summary() {
    local SUMMARY_FILE="${RESULT_DIR}/summary_report.txt"
    
    {
        echo "╔════════════════════════════════════════════════════════════════════════╗"
        echo "║         SPARC Cluster Benchmark Summary                                ║"
        echo "╚════════════════════════════════════════════════════════════════════════╝"
        echo
        echo "Job ID: $JOB_ID"
        echo "Date: $(date)"
        echo "Threads: $NUM_THREADS"
        echo
        echo "Results Directory: $RESULT_DIR"
        echo
        echo "═══════════════════════════════════════════════════════════════════════════"
        echo "Performance Summary (Average times in seconds)"
        echo "═══════════════════════════════════════════════════════════════════════════"
        echo
        
        printf "%-15s" "Implementation"
        for N in "${PARTICLE_COUNTS[@]}"; do
            printf " | %10s" "N=$N"
        done
        echo
        
        printf "%-15s" "───────────────"
        for N in "${PARTICLE_COUNTS[@]}"; do
            printf " | %10s" "──────────"
        done
        echo
        
        for impl in python serial optimized fastmath parallel_omp par_unseq; do
            RESULTS_FILE="${RESULT_DIR}/${impl}_results.csv"
            
            if [ ! -f "$RESULTS_FILE" ]; then
                continue
            fi
            
            printf "%-15s" "$impl"
            
            for N in "${PARTICLE_COUNTS[@]}"; do
                AVG=$(awk -F, -v n="$N" '$1==n {sum+=$3; count++} END {if(count>0) printf "%.3f", sum/count; else print "N/A"}' "$RESULTS_FILE")
                printf " | %10s" "$AVG"
            done
            echo
        done
        
        echo
        echo "═══════════════════════════════════════════════════════════════════════════"
        
    } > "$SUMMARY_FILE"
    
    cat "$SUMMARY_FILE"
    echo
    echo "✓ Summary saved to: $SUMMARY_FILE"
}

generate_summary

################################################################################
# Optional: Run Intel Advisor profiling
################################################################################

if command -v advixe-cl &> /dev/null; then
    echo
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "Intel Advisor detected - Running profiling analysis"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo
    
    # Run advisor profiling script if available
    if [ -f "profile_with_advisor.sh" ]; then
        bash profile_with_advisor.sh
        
        # Move profiling results to job results directory
        if [ -d "profiling_results" ]; then
            mv profiling_results "${RESULT_DIR}/"
        fi
    fi
fi

################################################################################
# Cleanup and finalization
################################################################################

echo
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Benchmark Complete!"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "All results saved in: $RESULT_DIR/"
echo
echo "Key files:"
echo "  • system_info.txt - System configuration"
echo "  • summary_report.txt - Performance summary"
echo "  • *_results.csv - Detailed timing data"
echo
echo "To analyze results:"
echo "  cat $RESULT_DIR/summary_report.txt"
echo "  python analyze_cluster_results.py $RESULT_DIR"
echo
echo "Job completed at: $(date)"
echo

# Create completion marker
touch "${RESULT_DIR}/COMPLETE"
