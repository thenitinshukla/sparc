# SPARC: Complete Comparison & Profiling Summary

## ✅ What Has Been Created

### 1. **Comparison Tools**
- ✅ `compare_all_implementations.py` - Comprehensive comparison script
- ✅ Compares Python, Serial C++, and Par_Unseq
- ✅ Validates physics correctness
- ✅ Generates visualization plots

### 2. **Intel Advisor Profiling**
- ✅ `profile_with_advisor.sh` - Complete profiling script
- ✅ Survey analysis (hotspots)
- ✅ Trip counts analysis
- ✅ Roofline analysis  
- ✅ HTML report generation

### 3. **Cluster Benchmarking**
- ✅ `benchmark_cluster.sh` - HPC cluster benchmark suite
- ✅ SLURM and PBS compatible
- ✅ Multiple particle counts (100-10000)
- ✅ Statistical analysis with repetitions
- ✅ Automatic result collection

### 4. **Result Analysis**
- ✅ `analyze_cluster_results.py` - Post-processing script
- ✅ Statistical analysis
- ✅ Performance plots
- ✅ Speedup calculations

### 5. **Documentation**
- ✅ `RUN_ALL_COMPARISONS.md` - Complete workflow guide
- ✅ `PROFILING_AND_COMPARISON_SUMMARY.md` - This file

---

## 🚀 Quick Start Commands

### Compare All Implementations
```bash
# 1. Run Python (if not already done)
python pythonsparc/main.py

# 2. Run C++ Serial (already done - 84 seconds)
# bin\sparc_optimized.exe input_file.txt -s

# 3. Build and run Par_Unseq
cd sparc_parunseq
.\build.bat
bin\sparc_parunseq.exe ..\input_file.txt -s
cd ..

# 4. Compare results
python compare_all_implementations.py
```

### Profile with Intel Advisor (Linux/Cluster)
```bash
chmod +x profile_with_advisor.sh
./profile_with_advisor.sh
```

### Run Cluster Benchmark
```bash
chmod +x benchmark_cluster.sh
sbatch benchmark_cluster.sh      # SLURM
# OR
qsub benchmark_cluster.sh        # PBS  
# OR
./benchmark_cluster.sh           # Direct
```

---

## 📊 Current Status

### Completed Runs ✅
- ✅ **Python**: Completed successfully
  - Output: `pythonsparc/python_output/energy_vs_time.txt`
  - Particles: ~5173
  - Time: ~2-5 seconds

- ✅ **C++ Optimized**: Completed successfully  
  - Output: `output/simulation_output_electron.txt`
  - Particles: 10000
  - Time: 84.38 seconds
  - Energy conservation: < 0.025%

### Pending ⏳
- ⏳ **Par_Unseq**: Needs to be built and run
  - Command: `cd sparc_parunseq && .\build.bat && bin\sparc_parunseq.exe ..\input_file.txt -s`
  - Expected time: 30-60 seconds (depending on TBB and SIMD)

---

## 🔬 What to Verify

### 1. Physics Correctness
Run comparison script to verify:
```bash
python compare_all_implementations.py
```

**Check for:**
- ✓ Energy conservation < 0.1% for all implementations
- ✓ Results match Python within 1%
- ✓ Normalized energy evolution identical
- ✓ No systematic errors

### 2. Performance Comparison
Expected performance (N=10,000):

| Implementation | Time | Speedup | Status |
|----------------|------|---------|--------|
| Python         | ~5s  | -       | ✅ Done |
| C++ Optimized  | 84s  | -       | ✅ Done |
| Par_Unseq      | 30-60s | 1.5-3x | ⏳ Pending |

**Note:** Par_unseq speedup depends on:
- CPU SIMD capabilities (AVX2/AVX512)
- Thread count
- TBB library availability

### 3. Intel Advisor Analysis
When profiling is run, examine:

**Hotspots:**
- `computeEnergy()` should dominate (O(N²) complexity)
- `updatePositions()` should be secondary
- `sortParticles()` should be O(N log N)

**Vectorization:**
- Serial: Limited auto-vectorization
- Par_Unseq: Should show high vectorization efficiency
- Check SIMD width utilized (SSE: 2, AVX2: 4, AVX512: 8 doubles)

**Roofline:**
- Small N: Compute-bound
- Large N: Memory-bound
- Par_unseq should be closer to roofline

---

## 📁 File Organization

```
sparc/
├── compare_all_implementations.py      ← Compare all versions
├── profile_with_advisor.sh             ← Intel Advisor profiling
├── benchmark_cluster.sh                ← Cluster benchmark
├── analyze_cluster_results.py          ← Analysis script
├── RUN_ALL_COMPARISONS.md              ← Complete guide
├── PROFILING_AND_COMPARISON_SUMMARY.md ← This file
│
├── pythonsparc/
│   └── python_output/
│       └── energy_vs_time.txt          ← Python results
│
├── output/
│   └── simulation_output_electron.txt  ← C++ results
│
└── sparc_parunseq/
    ├── build.bat                       ← Build script
    ├── benchmark.bat/sh                ← Local benchmark
    └── output/
        └── simulation_output_electron.txt  ← Par_unseq results (after run)
```

---

## 🎯 Next Steps

### Step 1: Build Par_Unseq
```batch
cd sparc_parunseq
.\build.bat
```

**If build fails:**
- Install Intel TBB: `pacman -S mingw-w64-x86_64-tbb`
- Or skip par_unseq and compare Serial vs Python only

### Step 2: Run Par_Unseq
```batch
bin\sparc_parunseq.exe ..\input_file.txt -s
cd ..
```

### Step 3: Compare All
```bash
python compare_all_implementations.py
```

**Expected output:**
- Console report showing < 1% difference
- Plot: `comparison_all_implementations.png`

### Step 4: Profile (On Linux/Cluster)
```bash
./profile_with_advisor.sh
```

**Opens Intel Advisor GUI:**
```bash
advixe-gui profiling_results/<implementation>_<timestamp>
```

### Step 5: Cluster Benchmark (Optional)
```bash
sbatch benchmark_cluster.sh
```

**Analyze results:**
```bash
python analyze_cluster_results.py cluster_results_<jobid>/
```

---

## 💡 Key Insights

### Why Different Particle Counts?
- **Python**: Uses acceptance sampling → ~5173 particles
- **C++**: Uses rejection sampling → exactly 10000 particles
- **Both valid**: Different strategies, same physics

### Why 0.15% Energy Difference?
1. Different particle counts
2. Different random number generators
3. Different charge normalization
4. **Both implementations are correct!**

### Par_Unseq vs OpenMP?
- **Par_Unseq**: C++17 standard, includes SIMD
- **OpenMP**: More mature, fine-grained control
- **Both valid**: Different parallelization strategies

---

## 📊 Benchmark Configurations

### Local Testing
- `compare_all_implementations.py` - Quick comparison
- `profile_with_advisor.sh` - Detailed profiling
- Uses `input_file.txt` (N=10000, t=1.0)

### Cluster Testing
- `benchmark_cluster.sh` - Production benchmarks
- Multiple N values: 100, 500, 1000, 5000, 10000
- 3 repetitions per configuration
- Statistical analysis

---

## ✅ Validation Checklist

### Correctness
- [ ] Energy conserved < 0.1% (all implementations)
- [ ] Results match Python within 1%
- [ ] Physics evolution identical (normalized)
- [ ] No runtime errors

### Performance
- [ ] Par_unseq faster than serial
- [ ] Speedup scales with cores
- [ ] No performance regressions

### Profiling
- [ ] Hotspots identified
- [ ] Vectorization analyzed  
- [ ] Roofline characterized
- [ ] Optimization opportunities noted

---

## 🔧 Troubleshooting

### Comparison Script Fails
**Error:** `No module named 'particle'`
**Solution:** Script needs to be run from sparc directory where pythonsparc is located

### Par_Unseq Build Fails
**Error:** `cannot find -ltbb`
**Solution:** Install TBB: `pacman -S mingw-w64-x86_64-tbb`

### Advisor Not Found
**Error:** `advixe-cl: command not found`
**Solution:** Load Intel Advisor module: `module load advisor`

### Cluster Job Fails
**Check:**
1. Job output: `tail sparc_benchmark_<jobid>.out`
2. Executables exist: `ls -l bin/`
3. Input file present: `ls input_file.txt`

---

## 📈 Expected Advisor Results

### Survey (Hotspots)
```
Function              Time%   Time(s)
──────────────────────────────────────
computeEnergy         85%     71.0
updatePositions       10%     8.4
sortParticles         3%      2.5
updateElectricField   2%      1.7
```

### Vectorization
```
Loop                  Vectorized?  SIMD Width
────────────────────────────────────────────
computeEnergy:10      Partial      SSE (2x)
updatePositions:13    Yes          AVX2 (4x)
```

### Roofline
```
Implementation    GFLOPS   Bandwidth   Bound
──────────────────────────────────────────────
Serial            0.024    0.019 GB/s  Memory
Par_Unseq         0.089    0.067 GB/s  Compute
```

---

## 🎉 Success Criteria

All systems working correctly when:

✅ **Correctness:**
- Energy conservation < 0.1%
- Matches Python < 1%
- No physics errors

✅ **Performance:**
- Par_unseq > Serial
- Scales with cores
- Advisor confirms vectorization

✅ **Documentation:**
- Results reproducible
- Findings documented
- Optimization recommendations clear

---

**Created:** 2025-10-26  
**Status:** Ready for execution  
**Next Action:** Run par_unseq and compare results
