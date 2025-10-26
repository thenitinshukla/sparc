#!/bin/bash
################################################################################
# SPARC Par_Unseq Benchmark Script
# Benchmarks the parallel unsequenced implementation with various configurations
################################################################################

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║         SPARC Par_Unseq Benchmark Suite                                ║"
echo "║         std::execution::par_unseq (SIMD + Multi-threaded)              ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if executable exists
EXEC="bin/sparc_parunseq"
if [ -f "bin/sparc_parunseq.exe" ]; then
    EXEC="bin/sparc_parunseq.exe"
fi

if [ ! -f "$EXEC" ]; then
    echo -e "${RED}ERROR: sparc_parunseq executable not found${NC}"
    echo "Please build it first: ./build.sh or build.bat"
    exit 1
fi

# Create results directory
mkdir -p results

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULT_FILE="results/benchmark_${TIMESTAMP}.txt"

echo "Results will be saved to: $RESULT_FILE"
echo

################################################################################
# Function to run a single benchmark
################################################################################
run_benchmark() {
    local N=$1
    local DESC=$2
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Benchmark: $DESC (N=$N particles)${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Create temporary input file
    cat > temp_input.txt <<EOF
N = $N
R = 1.0
dt = 0.001
tend = 0.1
SAVE_INTERVAL = 10
species electron  1.0
EOF

    # Run benchmark
    echo "Running simulation..."
    START_TIME=$(date +%s.%N)
    
    $EXEC temp_input.txt -n > temp_output.txt 2>&1
    
    END_TIME=$(date +%s.%N)
    ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
    
    # Extract results
    ENERGY_DRIFT=$(grep -i "energy conservation error" temp_output.txt | tail -1 | awk '{print $(NF-1)}' || echo "N/A")
    
    # Display results
    echo -e "${GREEN}✓ Completed in ${ELAPSED} seconds${NC}"
    echo "  Energy conservation error: ${ENERGY_DRIFT}"
    
    # Save to results file
    {
        echo "=========================================="
        echo "Benchmark: $DESC"
        echo "Particles: $N"
        echo "Time: $ELAPSED seconds"
        echo "Energy drift: $ENERGY_DRIFT"
        echo "Timestamp: $(date)"
        echo "=========================================="
        echo
    } >> "$RESULT_FILE"
    
    # Cleanup
    rm -f temp_input.txt temp_output.txt
    echo
}

################################################################################
# Main Benchmark Suite
################################################################################

# Initialize results file
{
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║         SPARC Par_Unseq Benchmark Results                              ║"
    echo "║         std::execution::par_unseq (SIMD + Multi-threaded)              ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo
    echo "Date: $(date)"
    echo "System: $(uname -a || echo 'Windows')"
    echo "Compiler: $(g++ --version | head -1)"
    echo
} > "$RESULT_FILE"

echo -e "${YELLOW}Starting benchmark suite...${NC}"
echo

# Run benchmarks with different particle counts
run_benchmark 100    "Small scale test"
run_benchmark 500    "Medium scale test"
run_benchmark 1000   "Large scale test"
run_benchmark 5000   "Production scale test"

################################################################################
# Comparative Benchmark
################################################################################

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Comparative Analysis (N=1000)${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════════════${NC}"
echo

# Create test input
cat > temp_input.txt <<EOF
N = 1000
R = 1.0
dt = 0.001
tend = 0.1
SAVE_INTERVAL = 10
species electron  1.0
EOF

echo "┌────────────────────────┬──────────────┬─────────────┐"
echo "│ Implementation         │ Time (s)     │ Speedup     │"
echo "├────────────────────────┼──────────────┼─────────────┤"

# Reference: Serial (from parent directory)
SERIAL_EXEC="../bin/sparc_serial"
[ -f "../bin/sparc_serial.exe" ] && SERIAL_EXEC="../bin/sparc_serial.exe"

if [ -f "$SERIAL_EXEC" ]; then
    START=$(date +%s.%N)
    $SERIAL_EXEC temp_input.txt -n > /dev/null 2>&1
    END=$(date +%s.%N)
    SERIAL_TIME=$(echo "$END - $START" | bc)
    
    printf "│ %-22s │ %12.3f │ %11s │\n" "Serial (-O2)" "$SERIAL_TIME" "1.00x"
fi

# Optimized (from parent directory)
OPT_EXEC="../bin/sparc_optimized"
[ -f "../bin/sparc_optimized.exe" ] && OPT_EXEC="../bin/sparc_optimized.exe"

if [ -f "$OPT_EXEC" ]; then
    START=$(date +%s.%N)
    $OPT_EXEC temp_input.txt -n > /dev/null 2>&1
    END=$(date +%s.%N)
    OPT_TIME=$(echo "$END - $START" | bc)
    SPEEDUP=$(echo "$SERIAL_TIME / $OPT_TIME" | bc -l)
    
    printf "│ %-22s │ %12.3f │ %10.2fx │\n" "Optimized (-O3)" "$OPT_TIME" "$SPEEDUP"
fi

# Parallel OpenMP (from parent directory)
PAR_EXEC="../bin/sparc_parallel"
[ -f "../bin/sparc_parallel.exe" ] && PAR_EXEC="../bin/sparc_parallel.exe"

if [ -f "$PAR_EXEC" ]; then
    START=$(date +%s.%N)
    $PAR_EXEC temp_input.txt -n > /dev/null 2>&1
    END=$(date +%s.%N)
    PAR_TIME=$(echo "$END - $START" | bc)
    SPEEDUP=$(echo "$SERIAL_TIME / $PAR_TIME" | bc -l)
    
    printf "│ %-22s │ %12.3f │ %10.2fx │\n" "Parallel (OpenMP)" "$PAR_TIME" "$SPEEDUP"
fi

# Par_Unseq (current implementation)
START=$(date +%s.%N)
$EXEC temp_input.txt -n > /dev/null 2>&1
END=$(date +%s.%N)
PAR_UNSEQ_TIME=$(echo "$END - $START" | bc)
SPEEDUP=$(echo "$SERIAL_TIME / $PAR_UNSEQ_TIME" | bc -l)

printf "│ %-22s │ %12.3f │ %10.2fx │\n" "Par_Unseq (C++17)" "$PAR_UNSEQ_TIME" "$SPEEDUP"

echo "└────────────────────────┴──────────────┴─────────────┘"

# Cleanup
rm -f temp_input.txt

echo
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Benchmark Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo
echo "Results saved to: $RESULT_FILE"
echo
echo "Summary:"
echo "  • Par_Unseq uses std::execution::par_unseq policy"
echo "  • Combines SIMD vectorization with multi-threading"
echo "  • Expected speedup: 2-8x depending on hardware"
echo
