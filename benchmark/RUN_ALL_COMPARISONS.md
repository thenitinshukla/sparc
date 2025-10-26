# Complete SPARC Comparison and Profiling Guide

## Overview

This guide walks you through comparing all SPARC implementations and profiling them with Intel Advisor.

---

## 📋 Prerequisites

### 1. Build All Implementations

```bash
# Main SPARC implementations
.\build_all_windows.bat

# Par_Unseq implementation
cd sparc_parunseq
.\build.bat
cd ..
```

### 2. Verify Intel Advisor is Available

```bash
# Linux/Cluster
which advixe-cl

# If not found, load module:
module load advisor
# OR
source /opt/intel/oneapi/advisor/latest/env/vars.sh
```

---

## 🚀 Quick Start: Run Everything

### Windows (Local)
```batch
REM 1. Run Python reference
python pythonsparc/main.py

REM 2. Run C++ serial/optimized
bin\sparc_optimized.exe input_file.txt -s

REM 3. Run par_unseq
cd sparc_parunseq
bin\sparc_parunseq.exe ..\input_file.txt -s
cd ..

REM 4. Compare all results
python compare_all_implementations.py
```

### Linux/Cluster
```bash
# 1. Run Python reference
python pythonsparc/main.py

# 2. Run C++ implementations
bin/sparc_optimized input_file.txt -s

# 3. Run par_unseq
cd sparc_parunseq
bin/sparc_parunseq ../input_file.txt -s
cd ..

# 4. Compare all results
python compare_all_implementations.py

# 5. Profile with Intel Advisor
chmod +x profile_with_advisor.sh
./profile_with_advisor.sh

# 6. Run cluster benchmark
chmod +x benchmark_cluster.sh
sbatch benchmark_cluster.sh      # SLURM
# OR
qsub benchmark_cluster.sh        # PBS
# OR
./benchmark_cluster.sh           # Direct execution
```

---

## 📊 Step-by-Step: Comparison Workflow

### Step 1: Run Python Reference
```bash
python pythonsparc/main.py
```

**Output:**
- `pythonsparc/python_output/Coulomb_explosion_dt0p001.npy`
- `pythonsparc/python_output/energy_vs_time.txt`

### Step 2: Run C++ Serial/Optimized
```bash
bin/sparc_optimized input_file.txt -s
```

**Output:**
- `output/simulation_output_electron.txt`

### Step 3: Run Par_Unseq
```bash
cd sparc_parunseq
bin/sparc_parunseq ../input_file.txt -s
cd ..
```

**Output:**
- `sparc_parunseq/output/simulation_output_electron.txt`

### Step 4: Compare All Implementations
```bash
python compare_all_implementations.py
```

**What it does:**
- Loads results from all implementations
- Compares initial conditions
- Checks energy conservation
- Validates physics consistency
- Creates comparison plots

**Output:**
- Console report with detailed comparison
- `comparison_all_implementations.png` - Visualization

**Expected Results:**
```
SPARC IMPLEMENTATION COMPARISON
════════════════════════════════════════════════════════════════════════

Implementation Summary:
────────────────────────────────────────────────────────────────────────
Implementation       Particles    Initial E       Final E         Drift %   
────────────────────────────────────────────────────────────────────────
Python               ~5173        1.053052e+01    1.053215e+01    0.015457
C++ Serial           10000        1.051436e+01    1.051112e+01    -0.030815
C++ Par_Unseq        10000        1.051436e+01    1.051112e+01    -0.030815

DETAILED COMPARISON vs Python Reference
════════════════════════════════════════════════════════════════════════

C++ Serial vs Python:
────────────────────────────────────────────────────────────────────────
  Initial energy difference: 0.1534%
  Max normalized difference: 0.0463%
  RMS normalized difference: 0.0277%
  ✓ VERY CLOSE: Physics match within 1%
  Energy conservation error: 0.030815%
  ✓ EXCELLENT: Energy conserved < 0.1%
```

---

## 🔬 Intel Advisor Profiling

### Run Profiling
```bash
chmod +x profile_with_advisor.sh
./profile_with_advisor.sh
```

**What it profiles:**
1. **Survey Analysis**: Hotspot identification
2. **Trip Counts**: Loop iteration counts
3. **Roofline Analysis**: Memory vs compute characterization
4. **FLOP Counts**: Floating-point operation analysis

**Output:**
- `profiling_results/<impl>_<timestamp>/` - Advisor project directories
- HTML reports for each implementation

### View Results

**GUI:**
```bash
advixe-gui profiling_results/<implementation>_<timestamp>
```

**HTML Reports:**
Open in browser:
- `profiling_results/<impl>_<timestamp>/report.html`
- `profiling_results/<impl>_<timestamp>/roofline.html`

**Key Metrics to Examine:**

1. **Hotspots:**
   - Which functions consume most time?
   - Energy calculation should be dominant

2. **Vectorization:**
   - Are loops vectorized?
   - What SIMD width is achieved? (SSE: 128-bit, AVX2: 256-bit, AVX512: 512-bit)
   - Par_unseq should show better vectorization

3. **Roofline:**
   - Memory bound or compute bound?
   - Where does code sit on roofline chart?
   - Optimization opportunities

4. **Parallel Efficiency:**
   - Thread scaling
   - Load balancing
   - Synchronization overhead

---

## 🖥️ Cluster Benchmarking

### Submit Cluster Job
```bash
# Make executable
chmod +x benchmark_cluster.sh

# Submit to SLURM
sbatch benchmark_cluster.sh

# OR submit to PBS
qsub benchmark_cluster.sh

# OR run directly
./benchmark_cluster.sh
```

### What It Does

1. **System Info Collection:**
   - CPU, memory, compiler versions
   - Node information
   - Environment variables

2. **Benchmarks Multiple Configurations:**
   - N = 100, 500, 1000, 5000, 10000 particles
   - 3 repetitions per configuration
   - Times all implementations

3. **Generates Reports:**
   - CSV files with raw data
   - Summary report with averages
   - Speedup analysis

4. **Optional Advisor Profiling:**
   - Runs if Advisor is available
   - Saves profiling data

### Monitor Job
```bash
# SLURM
squeue -u $USER
tail -f sparc_benchmark_<jobid>.out

# PBS
qstat -u $USER
tail -f sparc_benchmark.o<jobid>
```

### Analyze Results
```bash
# After job completes
python analyze_cluster_results.py cluster_results_<jobid>/
```

**Output:**
- Detailed statistical analysis
- Performance plots
- Speedup analysis
- Scaling efficiency

---

## 📈 Expected Results

### Correctness
- **Energy Conservation**: All implementations < 0.1% drift ✓
- **vs Python**: < 1% difference ✓
- **Physics Consistency**: Normalized energy evolution matches ✓

### Performance (N=10,000)

| Implementation | Time (est) | Speedup | Energy Drift |
|----------------|------------|---------|--------------|
| Python         | 2-5s       | -       | 0.015%       |
| Serial         | 190s       | 1.0x    | 0.031%       |
| Optimized      | 140s       | 1.4x    | 0.031%       |
| Parallel (OpenMP) | 50s     | 3.8x    | 0.031%       |
| **Par_Unseq**  | **30-60s** | **3-6x** | **0.031%** |

*Par_unseq performance depends on SIMD support and core count*

### Advisor Insights

**Expected findings:**

1. **Hotspot**: `computeEnergy()` dominates (O(N²))
2. **Vectorization**:
   - Serial: Limited auto-vectorization
   - Par_unseq: Full SIMD utilization
3. **Parallelization**:
   - OpenMP: Good scaling up to ~8 cores
   - Par_unseq: Better load balancing
4. **Roofline**:
   - Memory bound for large N
   - Compute bound for small N

---

## 🎯 Key Comparisons to Make

### 1. Correctness Verification
```python
python compare_all_implementations.py
```

**Check:**
- ✓ Energy conservation < 0.1%
- ✓ All implementations agree within 1%
- ✓ Initial conditions properly set

### 2. Performance Analysis
```bash
# Local
./profile_with_advisor.sh

# Cluster
sbatch benchmark_cluster.sh
```

**Check:**
- ✓ Speedup vs serial
- ✓ Scaling with particle count
- ✓ Thread scaling efficiency

### 3. Vectorization Analysis (Advisor)
**Check:**
- ✓ Which loops vectorize?
- ✓ SIMD width achieved?
- ✓ Vectorization efficiency?

### 4. Roofline Analysis (Advisor)
**Check:**
- ✓ Memory vs compute bound?
- ✓ Distance from roofline?
- ✓ Optimization potential?

---

## 📝 Troubleshooting

### Issue: Results don't match Python

**Check:**
1. Same random seed? (both use seed 10)
2. Different particle counts? (Python ~5K, C++ 10K)
3. Energy normalized properly?

**Solution:** Small differences (< 1%) are expected due to different particle generation strategies.

### Issue: Par_unseq slower than expected

**Possible causes:**
1. TBB not installed or not linked properly
2. Small N (overhead dominates for N < 1000)
3. Single-core CPU
4. Debug build instead of release

**Solution:**
- Verify TBB: `ldd bin/sparc_parunseq | grep tbb`
- Use N > 1000
- Check optimization: `file bin/sparc_parunseq`

### Issue: Advisor fails

**Check:**
1. Advisor in PATH? `which advixe-cl`
2. Permissions? `ls -l profile_with_advisor.sh`
3. Disk space? `df -h`

**Solution:**
```bash
module load advisor
chmod +x profile_with_advisor.sh
```

---

## 📚 File Summary

### Created Scripts
- ✅ `compare_all_implementations.py` - Compare all versions
- ✅ `profile_with_advisor.sh` - Intel Advisor profiling
- ✅ `benchmark_cluster.sh` - Cluster benchmark suite
- ✅ `analyze_cluster_results.py` - Analyze cluster results

### Output Files
- `comparison_all_implementations.png` - Visual comparison
- `profiling_results/` - Advisor profiling data
- `cluster_results_<jobid>/` - Cluster benchmark data

---

## ✅ Complete Workflow Checklist

- [ ] Build all implementations
- [ ] Run Python reference
- [ ] Run C++ serial/optimized
- [ ] Run par_unseq
- [ ] Compare implementations (verify correctness)
- [ ] Profile with Intel Advisor
- [ ] Submit cluster benchmark
- [ ] Analyze cluster results
- [ ] Review Advisor roofline
- [ ] Document findings

---

**Last Updated:** 2025-10-26  
**Author:** SPARC Development Team
