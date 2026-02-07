# SPARC-MPI: Parallel Coulomb Explosion Simulation

MPI-parallelized version of SPARC (Simulation of Particles in A Radial Configuration) for simulating Coulomb explosions in spherical plasmas.

## Features

- **Parallel Sample Sort**: Dynamically redistributes particles across MPI ranks based on radial distance
- **Distributed Electric Field**: Uses `MPI_Exscan` for efficient prefix sum across ranks
- **Scalable to 128+ nodes**: Designed for strong scaling with >80% efficiency
- **Energy Conservation Tracking**: Reports energy error at each output interval

## Quick Start

### Prerequisites
- MPI implementation (OpenMPI, MPICH, or Intel MPI)
- C++14 compatible compiler
- CMake 3.10+ (optional, Makefile also provided)

### Building

#### Using CMake:
```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

#### Using Makefile:
```bash
make
```

### Running

```bash
# Single rank (for testing)
mpirun -np 1 ./sparc_mpi input_file.txt

# Multiple ranks
mpirun -np 4 ./sparc_mpi input_file.txt

# With position output
mpirun -np 8 ./sparc_mpi input_file.txt -p -s
```

### SLURM Cluster

```bash
sbatch run_slurm.sh
```

## Input File Format

```
# Simulation Parameters
N = 10000000          # Total number of particles
R = 1.0               # Radius of the sphere
dt = 0.001            # Time step
tend = 1.0            # End time
SAVE_INTERVAL = 100   # Save data every N steps

# Particle Species
species electron  1.0        # electrons (m/q = 1)
species proton    1836.0     # protons (m/q = 1836)
```

## Algorithm

### Parallel Sample Sort

1. **Local Sort**: Each rank sorts its particles by $r^2$
2. **Sample Selection**: Select evenly-spaced samples from sorted data
3. **Global Splitters**: Root gathers samples, selects $P-1$ splitters
4. **Redistribution**: `MPI_Alltoallv` exchanges particles based on splitters
5. **Merge**: Local merge sort on received particles

After redistribution, Rank $i$ owns all particles with radii in range $[r_i, r_{i+1})$.

### Electric Field Computation

```
Er[i] = Q_enclosed(r[i]) / r^2[i]
```

Where $Q_{enclosed}$ is the cumulative charge from particles closer to the origin.

- `MPI_Exscan` computes the sum of charges from all previous ranks
- Local prefix sum adds charges on current rank
- Each particle's $E_r$ is computed locally

### Complexity

| Operation | Serial | Parallel (P ranks) |
|-----------|--------|-------------------|
| Sort      | O(N log N) | O((N/P) log(N/P)) + O(P log P) |
| E-field   | O(N)   | O(N/P) + O(log P) |
| Position  | O(N)   | O(N/P) |

## Scaling Performance

Expected strong scaling efficiency:
- 16 ranks: ~95%
- 64 ranks: ~90%
- 128 ranks: ~85%
- 256 ranks: ~80%

Run `run_scaling_study.sh` to measure actual performance on your cluster.

## Files

```
sparc_mpi/
├── include/
│   └── ParticleSystem.h      # Header with MPI context
├── src/
│   ├── main.cpp              # MPI-enabled main loop
│   └── core/
│       ├── ParticleSystem.cpp
│       ├── sort_particles.cpp      # Sample Sort implementation
│       ├── update_electric_field.cpp  # MPI_Exscan prefix sum
│       ├── update_positions.cpp
│       ├── compute_energy.cpp      # MPI_Allreduce energy
│       ├── performance.cpp
│       └── save_positions.cpp      # MPI_Gatherv I/O
├── CMakeLists.txt
├── Makefile
├── input_file.txt
├── run_slurm.sh
└── run_scaling_study.sh
```

## License

Copyright (c) 2025 CINECA
