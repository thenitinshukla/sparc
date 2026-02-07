#!/bin/bash
# Strong Scaling Study Script for SPARC-MPI
# Tests fixed problem size with increasing number of MPI processes

# Configuration
N=10000000  # 10 million particles
INPUT_TEMPLATE="input_file.txt"
OUTPUT_DIR="scaling_results"
EXECUTABLE="./sparc_mpi"

# Create output directory
mkdir -p $OUTPUT_DIR

# Generate input file with specified N
generate_input() {
    local n=$1
    cat > ${OUTPUT_DIR}/input_N${n}.txt << EOF
# Simulation Parameters
N = ${n}
R = 1.0
dt = 0.001
tend = 0.1
SAVE_INTERVAL = 10
MAX_SPECIES = 10
BUFFER_SIZE = 32768

# Particle Species
species electron  1.0
EOF
}

generate_input $N

# Strong scaling: fixed N, varying P
echo "=== Strong Scaling Study ===" | tee ${OUTPUT_DIR}/strong_scaling.log
echo "N = $N particles" | tee -a ${OUTPUT_DIR}/strong_scaling.log
echo "" | tee -a ${OUTPUT_DIR}/strong_scaling.log

for P in 2 4 8 16 32 64 112; do
    echo "Running with $P MPI processes..." | tee -a ${OUTPUT_DIR}/strong_scaling.log
    
    # Run and capture output
    mpirun -np $P $EXECUTABLE ${OUTPUT_DIR}/input_N${N}.txt -n 2>&1 | tee ${OUTPUT_DIR}/run_P${P}.out
    
    # Extract timing from output
    TIME=$(grep "Total execution time" ${OUTPUT_DIR}/run_P${P}.out | awk '{print $4}')
    
    echo "P=$P, Time=${TIME}s" | tee -a ${OUTPUT_DIR}/strong_scaling.log
    echo "" | tee -a ${OUTPUT_DIR}/strong_scaling.log
done

echo "Strong scaling study complete. Results in ${OUTPUT_DIR}/"

# Calculate speedup and efficiency
echo "" | tee -a ${OUTPUT_DIR}/strong_scaling.log
echo "=== Scaling Analysis ===" | tee -a ${OUTPUT_DIR}/strong_scaling.log
python3 << 'PYTHON_SCRIPT'
import re

# Read results
times = {}
with open("scaling_results/strong_scaling.log", "r") as f:
    for line in f:
        match = re.search(r"P=(\d+), Time=([0-9.]+)s", line)
        if match:
            p = int(match.group(1))
            t = float(match.group(2))
            times[p] = t

if times:
    t1 = times.get(1, times[min(times.keys())])
    p_base = 1 if 1 in times else min(times.keys())
    
    print(f"\n{'Ranks':>8} {'Time (s)':>12} {'Speedup':>10} {'Efficiency':>12}")
    print("-" * 45)
    
    for p in sorted(times.keys()):
        speedup = t1 / times[p] if times[p] > 0 else 0
        ideal_speedup = p / p_base
        efficiency = (speedup / ideal_speedup) * 100
        print(f"{p:>8} {times[p]:>12.3f} {speedup:>10.2f}x {efficiency:>11.1f}%")
PYTHON_SCRIPT
