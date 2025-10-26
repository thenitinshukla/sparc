# SPARC Par_Unseq Implementation

## Overview

This directory contains the **parallel unsequenced** implementation of SPARC using C++17 `std::execution::par_unseq` execution policies.

### Key Features
- ✅ **SIMD + Multi-threading**: Combines vectorization and parallelization
- ✅ **C++17 Standard**: Uses standard library parallel algorithms
- ✅ **Portable**: Works with any C++17 compiler supporting parallel algorithms
- ✅ **High Performance**: Expected 2-8x speedup over serial

---

## What is `std::execution::par_unseq`?

The `par_unseq` execution policy allows algorithms to execute:
1. **In parallel** (multi-threaded across CPU cores)
2. **Unsequenced** (vectorized using SIMD instructions)

Example:
```cpp
std::for_each(
    std::execution::par_unseq,  // ← Parallel + SIMD
    data.begin(), data.end(),
    [](auto& element) {
        // Distributed across threads AND vectorized
    }
);
```

---

## Building

### Windows
```batch
.\build.bat
```

### Linux/Mac
```bash
chmod +x build.sh
./build.sh
```

### Requirements
- **Compiler**: GCC 9+ or Clang 9+ with C++17 support
- **Library**: Intel TBB (Threading Building Blocks)

#### Installing TBB

**Windows (MSYS2):**
```bash
pacman -S mingw-w64-x86_64-tbb
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install libtbb-dev
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install tbb-devel
```

**macOS:**
```bash
brew install tbb
```

---

## Running

### Basic Execution
```batch
# Windows
bin\sparc_parunseq.exe ..\input_file.txt -s

# Linux/Mac
./bin/sparc_parunseq ../input_file.txt -s
```

### Run Benchmarks
```batch
# Windows
.\benchmark.bat

# Linux/Mac
./benchmark.sh
```

---

## Implementation Details

### Modified Algorithms

#### 1. Energy Calculation
**File:** `src/core/compute_energy.cpp`

Uses `std::transform_reduce` with `par_unseq`:
```cpp
double K = std::transform_reduce(
    std::execution::par_unseq,
    indices.begin(), indices.end(),
    0.0,
    std::plus<>(),
    [&](int i) { return 0.5 * mass * v²[i]; }
);
```

**Benefits:**
- Parallel reduction across threads
- SIMD vectorization of v² calculations
- Automatic load balancing

#### 2. Position Update
**File:** `src/core/update_positions.cpp`

Uses `std::for_each` with `par_unseq`:
```cpp
std::for_each(
    std::execution::par_unseq,
    indices.begin(), indices.end(),
    [&](int i) {
        v[i] += dt * a[i];
        x[i] += dt * v[i];
    }
);
```

**Benefits:**
- Independent operations → perfect parallelism
- SIMD vectorization of arithmetic
- No race conditions

#### 3. Particle Sorting
**File:** `src/core/sort_particles.cpp`

Uses parallel sort:
```cpp
std::sort(
    std::execution::par_unseq,
    indices.begin(), indices.end(),
    [&](int i, int j) { return r²[i] < r²[j]; }
);
```

**Benefits:**
- O(N log N) parallel merge sort
- Vectorized comparisons
- Work-efficient parallelization

#### 4. Electric Field
**File:** `src/core/update_electric_field.cpp`

**Challenge:** Cumulative sum is sequential!

**Solution:**
```cpp
// Sequential cumsum (unavoidable)
for (int i = 1; i < N; i++) {
    cumsum[i] = cumsum[i-1] + q[i];
}

// Parallel division
std::for_each(
    std::execution::par_unseq,
    indices.begin(), indices.end(),
    [&](int i) { E[i] = cumsum[i] / r²[i]; }
);
```

---

## Performance Expectations

### Speedup vs Serial

| Particle Count | Expected Speedup |
|----------------|------------------|
| 100            | 1.5-2x          |
| 1,000          | 2-4x            |
| 10,000         | 3-6x            |
| 100,000        | 4-8x            |

**Factors affecting speedup:**
- CPU core count (more cores = better)
- SIMD width (AVX512 > AVX2 > SSE)
- Memory bandwidth
- Cache size

### vs OpenMP Parallel

**Par_Unseq advantages:**
- SIMD vectorization included
- Better load balancing
- Standard C++ (more portable)

**OpenMP advantages:**
- More mature
- Fine-grained control
- May be faster for some workloads

---

## Troubleshooting

### Build Fails: TBB not found

**Error:**
```
cannot find -ltbb
```

**Solution:**
1. Install TBB (see Building section)
2. Or try without `-ltbb` flag (some compilers have built-in support)

### Runtime: Slower than expected

**Possible causes:**
1. **Particle count too small**: Need N > 1000 for overhead to be worth it
2. **Single core CPU**: Par_unseq needs multiple cores
3. **Memory bound**: Check memory bandwidth
4. **Debug build**: Use release build with `-O3`

**Solutions:**
- Use larger particle counts
- Check CPU core count: `nproc` (Linux) or Task Manager (Windows)
- Use optimized build flags

### Compilation: C++17 not supported

**Error:**
```
error: 'execution' is not a namespace-name
```

**Solution:**
- Update compiler to GCC 9+ or Clang 9+
- Or use the regular parallel version: `../bin/sparc_parallel.exe`

---

## Comparison with Other Implementations

| Implementation | Optimization | Parallelism | SIMD | Complexity |
|----------------|--------------|-------------|------|------------|
| Serial         | -O2          | None        | No   | Low        |
| Optimized      | -O3          | None        | Auto | Low        |
| Parallel       | -O3 -fopenmp | OpenMP      | No   | Medium     |
| **Par_Unseq**  | -O3 -std=c++17 | C++17     | **Yes** | Medium  |

---

## Files in This Directory

```
sparc_parunseq/
├── src/
│   ├── main.cpp                    # Copied from parent
│   ├── core/
│   │   ├── ParticleSystem.cpp      # Copied from parent
│   │   ├── compute_energy.cpp      # Modified for par_unseq
│   │   ├── sort_particles.cpp      # Modified for par_unseq
│   │   ├── update_electric_field.cpp # Modified for par_unseq
│   │   ├── update_positions.cpp    # Modified for par_unseq
│   │   ├── performance.cpp         # Copied from parent
│   │   └── save_positions.cpp      # Copied from parent
│   └── utils/
│       └── utils.cpp               # Copied from parent
├── include/
│   └── ParticleSystem.h            # Copied from parent
├── bin/
│   └── sparc_parunseq.exe          # Built executable
├── results/                        # Benchmark results
├── build.bat                       # Windows build script
├── build.sh                        # Linux/Mac build script
├── benchmark.bat                   # Windows benchmark
├── benchmark.sh                    # Linux/Mac benchmark
└── README.md                       # This file
```

---

## Next Steps

1. **Build**: `.\build.bat` or `./build.sh`
2. **Test**: Run with small N to verify
3. **Benchmark**: Compare with other implementations
4. **Optimize**: Tune for your hardware

---

## References

- [C++17 Parallel Algorithms](https://en.cppreference.com/w/cpp/algorithm)
- [Intel TBB Documentation](https://www.intel.com/content/www/us/en/developer/tools/oneapi/onetbb.html)
- [Execution Policies](https://en.cppreference.com/w/cpp/algorithm/execution_policy_tag_t)

---

**Author:** SPARC Development Team  
**Version:** 1.0  
**Date:** 2025-10-26
