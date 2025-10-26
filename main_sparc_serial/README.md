# SPARC: Simulation of Particles in A Radial Configuration
SPARC is a spherical plasma where the ions remain fixed in place. During a Coulomb explosion, the electrons repel each other due to their electric charges, creating shock-like shells as they expand. 
Instead of calculating the Coulomb force between individual particles, we solve the exact equations of motion to describe how each electron moves.

This is a C++ implementation of the SPARC project using Structure of Arrays (SoA) for improved performance.

## Project Structure

```
sparc/
├── include/                 # Header files
│   └── ParticleSystem.h     # Particle system class definition
├── src/                     # Source files
│   ├── core/                # Core simulation components
│   │   ├── ParticleSystem.cpp
│   │   ├── compute_energy.cpp
│   │   ├── sort_particles.cpp
│   │   ├── update_electric_field.cpp
│   │   ├── update_positions.cpp
│   │   └── performance.cpp
│   ├── utils/               # Utility functions
│   │   └── utils.cpp
│   ├── visualization/       # Visualization tools
│   │   ├── visualize.py     # Matplotlib visualization script
│   │   ├── simple_visualization.py
│   │   ├── final_visualization.py
│   │   └── visualization_2d.py
│   └── main.cpp             # Main program
├── build/                   # Build directory
├── input_file.txt           # Simulation parameters
├── makefile                 # Build script
├── build.bat                # Windows build script
├── CMakeLists.txt           # CMake configuration
├── requirements.txt         # Python dependencies
├── compare_results.py       # Comparison script
└── README.md                # This file
```

## Features

- **C++ Implementation**: Modern C++ implementation with object-oriented design
- **Structure of Arrays (SoA)**: Improved memory layout for better cache performance
- **Modular Design**: Well-organized code structure for maintainability
- **Complete Physics Simulation**: All core SPARC algorithms implemented
- **Visualization**: Python scripts for 2D/3D particle visualization

## Building the Project

### Windows

```bash
.\build.bat
```

### Linux/macOS with Make

```bash
make
```

### Using CMake

```bash
mkdir build
cd build
cmake ..
make
```

## Running the Simulation

```bash
.\sparc_cpp.exe input_file.txt [options]
```

### Options

- `-p`: Save particle positions
- `-s`: Save simulation data
- `-e`: Save energy distribution
- `-n`: Do not save any data

### Example

```bash
.\sparc_cpp.exe input_file.txt -p -s -e
```

When the `-p` and `-s` flags are used, results are automatically saved in an `output` folder.

## Input File Format

The input file defines simulation parameters:

```
# Simulation Parameters
N = 10000         # Total number of particles
R = 1.0           # Radius of the sphere
dt = 0.001        # Time step
tend = 1.0        # End time

# Particle Species
species electron  1.0        # Species 1: electrons
species ion       10.0       # Species 2: ions
species proton    1836.0     # Species 3: protons
```

## Output Files

- `simulation_output_<species>.txt`: Simulation data for each species
- Binary files for particle positions (when -p flag is used)
- Binary files for energy distribution (when -e flag is used)
