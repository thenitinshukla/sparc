#!/bin/bash
################################################################################
# Intel Advisor Profiling Script for SPARC
# Profiles all implementations with Intel Advisor
################################################################################

set -e

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║         SPARC Intel Advisor Profiling Suite                            ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo

# Check if Intel Advisor is available
if ! command -v advixe-cl &> /dev/null; then
    echo "ERROR: Intel Advisor not found in PATH"
    echo ""
    echo "Please ensure Intel Advisor is installed and loaded:"
    echo "  source /opt/intel/oneapi/advisor/latest/env/vars.sh"
    echo "  OR"
    echo "  module load advisor"
    exit 1
fi

echo "✓ Intel Advisor found: $(which advixe-cl)"
echo

# Create profiling results directory
PROF_DIR="profiling_results"
mkdir -p "$PROF_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

################################################################################
# Function to profile an implementation
################################################################################
profile_implementation() {
    local NAME=$1
    local EXEC=$2
    local ARGS=$3
    local RESULT_DIR="${PROF_DIR}/${NAME}_${TIMESTAMP}"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Profiling: $NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo

    if [ ! -f "$EXEC" ]; then
        echo "  ✗ Executable not found: $EXEC"
        echo "  Skipping..."
        echo
        return
    fi
    
    mkdir -p "$RESULT_DIR"
    
    # 1. Survey Analysis (hotspots)
    echo "  [1/4] Running Survey Analysis (hotspots)..."
    advixe-cl --collect=survey \
              --project-dir="$RESULT_DIR" \
              --search-dir src:=./src \
              --search-dir src:=./sparc_parunseq/src \
              -- $EXEC $ARGS > /dev/null 2>&1
    echo "  ✓ Survey complete"
    
    # 2. Trip Counts Analysis
    echo "  [2/4] Running Trip Counts Analysis..."
    advixe-cl --collect=tripcounts \
              --project-dir="$RESULT_DIR" \
              --search-dir src:=./src \
              --search-dir src:=./sparc_parunseq/src \
              --flop \
              -- $EXEC $ARGS > /dev/null 2>&1
    echo "  ✓ Trip counts complete"
    
    # 3. Roofline Analysis (performance characterization)
    echo "  [3/4] Running Roofline Analysis..."
    advixe-cl --collect=roofline \
              --project-dir="$RESULT_DIR" \
              --search-dir src:=./src \
              --search-dir src:=./sparc_parunseq/src \
              -- $EXEC $ARGS > /dev/null 2>&1
    echo "  ✓ Roofline complete"
    
    # 4. Generate report
    echo "  [4/4] Generating HTML report..."
    advixe-cl --report=survey \
              --project-dir="$RESULT_DIR" \
              --format=html \
              --report-output="${RESULT_DIR}/report.html" > /dev/null 2>&1
    
    # Generate roofline chart
    advixe-cl --report=roofline \
              --project-dir="$RESULT_DIR" \
              --format=html \
              --report-output="${RESULT_DIR}/roofline.html" > /dev/null 2>&1
    
    echo "  ✓ Reports generated"
    echo "  Results saved to: $RESULT_DIR"
    echo
}

################################################################################
# Create test input file
################################################################################
cat > profile_input.txt <<EOF
N = 1000
R = 1.0
dt = 0.001
tend = 0.1
SAVE_INTERVAL = 10
species electron  1.0
EOF

echo "Created profile_input.txt (N=1000, short run)"
echo

################################################################################
# Profile all implementations
################################################################################

# Serial
if [ -f "bin/sparc_serial" ] || [ -f "bin/sparc_serial.exe" ]; then
    SERIAL_EXEC="bin/sparc_serial"
    [ -f "bin/sparc_serial.exe" ] && SERIAL_EXEC="bin/sparc_serial.exe"
    profile_implementation "serial" "$SERIAL_EXEC" "profile_input.txt -n"
fi

# Optimized
if [ -f "bin/sparc_optimized" ] || [ -f "bin/sparc_optimized.exe" ]; then
    OPT_EXEC="bin/sparc_optimized"
    [ -f "bin/sparc_optimized.exe" ] && OPT_EXEC="bin/sparc_optimized.exe"
    profile_implementation "optimized" "$OPT_EXEC" "profile_input.txt -n"
fi

# Parallel (OpenMP)
if [ -f "bin/sparc_parallel" ] || [ -f "bin/sparc_parallel.exe" ]; then
    PAR_EXEC="bin/sparc_parallel"
    [ -f "bin/sparc_parallel.exe" ] && PAR_EXEC="bin/sparc_parallel.exe"
    export OMP_NUM_THREADS=4
    profile_implementation "parallel_omp" "$PAR_EXEC" "profile_input.txt -n"
fi

# Par_Unseq
if [ -f "sparc_parunseq/bin/sparc_parunseq" ] || [ -f "sparc_parunseq/bin/sparc_parunseq.exe" ]; then
    PARUNSEQ_EXEC="sparc_parunseq/bin/sparc_parunseq"
    [ -f "sparc_parunseq/bin/sparc_parunseq.exe" ] && PARUNSEQ_EXEC="sparc_parunseq/bin/sparc_parunseq.exe"
    profile_implementation "par_unseq" "$PARUNSEQ_EXEC" "../profile_input.txt -n"
fi

# Cleanup
rm -f profile_input.txt

################################################################################
# Summary
################################################################################

echo "═══════════════════════════════════════════════════════════════════════════"
echo "Intel Advisor Profiling Complete!"
echo "═══════════════════════════════════════════════════════════════════════════"
echo
echo "Results saved in: $PROF_DIR/"
echo
echo "To view results:"
echo "  advixe-gui $PROF_DIR/<implementation>_${TIMESTAMP}"
echo
echo "Or open HTML reports in browser:"
find "$PROF_DIR" -name "*.html" -type f | while read file; do
    echo "  file://$(realpath "$file")"
done
echo
echo "Key metrics to examine:"
echo "  • Hotspots: Which functions consume most time"
echo "  • Vectorization: Which loops are vectorized"
echo "  • Roofline: Memory vs compute bound analysis"
echo "  • Trip counts: Loop iteration counts"
echo
