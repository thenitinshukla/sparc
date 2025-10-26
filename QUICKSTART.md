# SPARC Quick Start Guide

This guide will help you quickly set up, build, run, and visualize SPARC simulations.

## Prerequisites

### Linux/macOS
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential cmake libtbb-dev python3 python3-pip

# macOS
brew install gcc cmake tbb python3

# Python packages
pip3 install numpy matplotlib pandas scipy pygame PyOpenGL
```

### Windows (MSYS2/MinGW)
```bash
# In MSYS2 terminal
pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-cmake mingw-w64-x86_64-tbb

# Python packages
pip install numpy matplotlib pandas scipy pygame PyOpenGL
```

## Quick Start (5 Minutes)

### 1. Build All Implementations

```bash
cd sparc

# Build serial version
cd main_sparc_serial
make clean && make
cd ..

# Build parallel version
cd sparc_parallel
make clean && make
cd ..

# Build par_unseq version
cd sparc_parunseq
make clean && make
cd ..

# Build memory pool version
cd sparc_memoryPool
make clean && make
cd ..
```

### 2. Run a Quick Test

```bash
# Run serial version (baseline)
cd main_sparc_serial
./sparc_cpp input_file.txt -p -s -e
cd ..

# Run parallel version (faster)
cd sparc_parallel
./sparc_parallel test_input.txt -p -s -e
cd ..
```

### 3. Visualize Results

```bash
# Real-time OpenGL animation
cd visualization
python opengl_realtime_animation.py ../sparc_parallel/output/

# Or matplotlib visualization
python visualize.py ../sparc_parallel/output/
```

## Running Benchmarks

### Local Machine

```bash
cd benchmark

# Quick benchmark (takes ~5 minutes)
python benchmark_runner.py

# Comprehensive comparison
python compare_all_results.py
```

### HPC Cluster (SLURM)

```bash
cd benchmark

# Submit cluster benchmark job
sbatch benchmark_cluster_all.sh

# Check results when complete
ls cluster_results_*/
```

## Comparison and Validation

```bash
cd benchmark

# Compare all implementations
python compare_all_results.py

# This will generate:
#   - energy_comparison.png
#   - position_comparison.png
#   - timing_comparison.png
#   - comparison_summary.txt
```

## Detailed Workflows

### Workflow 1: Single Implementation Test

```bash
# 1. Build
cd main_sparc_serial
make

# 2. Create custom input
cat > my_input.txt <<EOF
N = 5000
R = 1.0
dt = 0.001
tend = 0.5
SAVE_INTERVAL = 10
species electron 1.0
EOF

# 3. Run simulation
./sparc_cpp my_input.txt -p -s -e

# 4. Visualize
cd ../visualization
python opengl_realtime_animation.py ../main_sparc_serial/output/
```

### Workflow 2: Performance Comparison

```bash
# 1. Build all implementations
cd sparc
for dir in main_sparc_serial sparc_std sparc_memoryPool sparc_parallel sparc_parunseq; do
    echo "Building $dir..."
    cd $dir && make clean && make && cd ..
done

# 2. Run benchmark suite
cd benchmark
./benchmark.sh

# 3. Analyze results
python visualize_benchmarks.py
python compare_all_results.py
```

### Workflow 3: Cluster Scaling Study

```bash
# 1. Build on cluster login node
cd sparc/sparc_parallel
module load gcc cmake
make clean && make

# 2. Submit scaling job
cd ../benchmark
sbatch benchmark_cluster_all.sh

# 3. When complete, analyze
python analyze_cluster_results.py cluster_results_JOBID/benchmark_data_*.csv
```

### Workflow 4: Create Publication-Quality Animations

```bash
# 1. Run simulation with frequent output
cd sparc_parallel
cat > anim_input.txt <<EOF
N = 10000
R = 1.0
dt = 0.0005
tend = 1.0
SAVE_INTERVAL = 5
species electron 1.0
EOF

./sparc_parallel anim_input.txt -p

# 2. Generate high-quality animation
cd ../visualization

# Real-time preview
python opengl_realtime_animation.py ../sparc_parallel/output/

# Create GIF (press 'A' to auto-capture frames)
python create_gif.py ../sparc_parallel/output/ sparc_explosion.gif --fps 30

# Or create video
python create_high_quality_animation.py ../sparc_parallel/output/ sparc_explosion.mp4
```

## Input File Format

### Basic Input
```
# Simulation parameters
N = 10000              # Number of particles
R = 1.0                # Initial sphere radius
dt = 0.001             # Time step
tend = 1.0             # End time
SAVE_INTERVAL = 10     # Save every N steps

# Particle species
species electron 1.0   # Name and mass ratio
```

### Multi-Species Input
```
N = 10000
R = 1.0
dt = 0.001
tend = 0.5
SAVE_INTERVAL = 10

# Multiple species
species electron  1.0      # Light particles (electrons)
species proton    1836.0   # Heavy particles (protons)
species positron  1.0      # Anti-particles
```

### High-Precision Input
```
N = 100000
R = 1.0
dt = 0.0001            # Smaller timestep for accuracy
tend = 0.1
SAVE_INTERVAL = 100

species electron 1.0
```

## Command-Line Options

All C++ implementations support:

- `-p` : Save particle positions to binary files
- `-s` : Save simulation data (time, energy, max radius)
- `-e` : Save energy distribution
- `-n` : No file output (benchmark mode)

Examples:
```bash
# Save everything
./sparc_cpp input.txt -p -s -e

# Benchmark mode (fastest)
./sparc_cpp input.txt -n

# Just simulation data
./sparc_cpp input.txt -s
```

## Troubleshooting

### Build Errors

**Error: "TBB not found"**
```bash
# Ubuntu
sudo apt install libtbb-dev

# macOS
brew install tbb

# Then rebuild
make clean && make
```

**Error: "OpenMP not supported"**
```bash
# Use GCC instead of Clang
export CXX=g++
make clean && make
```

### Runtime Errors

**Segmentation fault**
- Check input file format
- Verify particle count is reasonable (< 1 million for desktop)
- Increase stack size: `ulimit -s unlimited`

**Slow performance**
- Use parallel implementation for N > 10000
- Set thread count: `export OMP_NUM_THREADS=8`
- Enable optimization: Rebuild with `-O3` flag

**Energy conservation error too large**
- Reduce time step (`dt`)
- Check if particles escaped to infinity
- Verify sorting is working

### Visualization Issues

**OpenGL window not opening**
```bash
# Install PyOpenGL and pygame
pip install pygame PyOpenGL PyOpenGL-accelerate

# On Linux, may need:
sudo apt install python3-opengl freeglut3-dev
```

**Animation too slow**
- Reduce particle count in visualization
- Lower FPS: modify `FPS = 30` in script
- Disable trails: press 'T' in viewer

## Performance Tips

### For Desktop/Laptop (< 8 cores)
- Use `sparc_parallel` or `sparc_parunseq`
- Set `OMP_NUM_THREADS=4` (or your core count)
- N < 50,000 particles recommended

### For Workstation (8-16 cores)
- Use `sparc_parallel` with `OMP_NUM_THREADS=8-16`
- N up to 100,000 particles
- Memory pool version gives 20-30% speedup

### For HPC Cluster (32+ cores)
- Use cluster benchmark script
- Test weak scaling (increase N with threads)
- Monitor memory usage for large N

## Verification

To verify your installation works:

```bash
# Quick test (should complete in < 30 seconds)
cd sparc/main_sparc_serial
./sparc_cpp input_file.txt -n

# If you see "Energy conservation error: < 0.001%", it's working!
```

## Next Steps

1. **Read the documentation**: `ReadTheDocs.md` for detailed information
2. **Run benchmarks**: Compare performance on your system
3. **Experiment**: Modify parameters, try different particle counts
4. **Visualize**: Create animations of your simulations
5. **Optimize**: Profile and tune for your hardware

## Getting Help

- Check `ReadTheDocs.md` for detailed documentation
- Review example input files in `testcase/`
- Look at benchmark scripts in `benchmark/`
- Check visualization examples in `visualization/`

## Common Use Cases

### 1. Quick Physics Test
```bash
cd main_sparc_serial
./sparc_cpp input_file.txt -s
grep "Energy" output/*.txt
```

### 2. Performance Benchmark
```bash
cd benchmark
time ./benchmark.sh > results.txt
```

### 3. Create Demo Video
```bash
cd visualization
python opengl_realtime_animation.py ../sparc_parallel/output/
# Press 'A' to start recording, 'A' again to stop
```

### 4. Large-Scale Simulation
```bash
cd sparc_parallel
export OMP_NUM_THREADS=16
./sparc_parallel large_input.txt -p -s
```

## Directory Structure Reference

```
sparc/
├── ReadTheDocs.md           # Comprehensive documentation
├── QUICKSTART.md            # This file
├── main_sparc_serial/       # Serial C++ implementation
├── sparc_std/               # Standard C++ version
├── sparc_memoryPool/        # With custom allocator
├── sparc_parallel/          # OpenMP parallel version
├── sparc_parunseq/          # C++17 par_unseq version
├── pythonsparc/             # Python reference
├── visualization/           # Visualization tools
│   ├── opengl_realtime_animation.py  # OpenGL viewer
│   ├── visualize.py         # Matplotlib plots
│   └── create_gif.py        # Animation export
├── benchmark/               # Benchmarking tools
│   ├── benchmark_cluster_all.sh  # Cluster submission script
│   ├── compare_all_results.py    # Results comparison
│   └── benchmark_runner.py       # Local benchmarks
└── testcase/                # Example inputs
```

## Success Criteria

Your installation is successful if:

✅ All implementations compile without errors
✅ Test simulation runs and reports energy error < 0.001%
✅ Benchmark completes and shows speedup for parallel versions
✅ Visualization opens and displays particles
✅ Results are consistent across implementations

---

**Questions?** Check `ReadTheDocs.md` or review the example scripts in `benchmark/` and `visualization/`.

**Ready to start?** Begin with Step 1: Build All Implementations (above)
