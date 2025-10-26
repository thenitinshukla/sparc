#!/bin/bash
# benchmark_cluster_all.sh
# Full corrected benchmark script

RESULTS_DIR="./cluster_results_"
mkdir -p "$RESULTS_DIR"

# Input sizes
SERIAL_SIZES=(1000 5000 10000 50000 100000)
PARALLEL_SIZES=(1000 5000 10000 50000 100000)
THREADS=(1 2 4 8 16 32)

# Executables
SERIAL_EXEC="./main_sparc_serial/sparc_cpp"
STD_EXEC="./sparc_std/sparc_cpp"
MEMPOOL_EXEC="./sparc_memoryPool/sparc_mempool"
PARALLEL_EXEC="./sparc_parallel/sparc_parallel"
PARUNSEQ_EXEC="./sparc_parunseq/sparc_parunseq"

# Check executables
for exec in "$SERIAL_EXEC" "$STD_EXEC" "$MEMPOOL_EXEC" "$PARALLEL_EXEC" "$PARUNSEQ_EXEC"; do
    if [[ ! -x "$exec" ]]; then
        echo "[ERROR] Executable not found: $exec"
    fi
done

# Run serial benchmarks
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Serial Benchmarks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for N in "${SERIAL_SIZES[@]}"; do
    INPUT="$RESULTS_DIR/input_serial_${N}.txt"
    if [[ ! -f "$INPUT" ]]; then
        echo "[WARNING] Input file not found: $INPUT. Creating dummy input."
        echo "$N" > "$INPUT"  # simple dummy input
    fi

    echo "[INFO] Running serial N=$N"
    [[ -x "$SERIAL_EXEC" ]] && "$SERIAL_EXEC" "$INPUT" > "$RESULTS_DIR/output_serial_${N}.txt"
    [[ -x "$STD_EXEC" ]] && "$STD_EXEC" "$INPUT" > "$RESULTS_DIR/output_std_${N}.txt"
    [[ -x "$MEMPOOL_EXEC" ]] && "$MEMPOOL_EXEC" "$INPUT" > "$RESULTS_DIR/output_mempool_${N}.txt"
done

# Run parallel benchmarks
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Parallel Benchmarks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for N in "${PARALLEL_SIZES[@]}"; do
    for T in "${THREADS[@]}"; do
        INPUT="$RESULTS_DIR/input_parallel_${N}_${T}.txt"
        if [[ ! -f "$INPUT" ]]; then
            echo "[WARNING] Input file not found: $INPUT. Creating dummy input."
            echo "$N $T" > "$INPUT"
        fi

        echo "[INFO] Running parallel N=$N, threads=$T"
        [[ -x "$PARALLEL_EXEC" ]] && "$PARALLEL_EXEC" "$INPUT" "$T" > "$RESULTS_DIR/output_parallel_${N}_${T}.txt"
        [[ -x "$PARUNSEQ_EXEC" ]] && "$PARUNSEQ_EXEC" "$INPUT" "$T" > "$RESULTS_DIR/output_parunseq_${N}_${T}.txt"
    done
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Benchmark Complete"
echo "Results directory: $RESULTS_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

