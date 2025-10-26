cmake_minimum_required(VERSION 3.10)
project(sparc_parallel)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall")

# Find OpenMP
find_package(OpenMP REQUIRED)

# Include directories
include_directories(include)

# Source files
set(CORE_SOURCES
    src/core/ParticleSystemParallel.cpp
    src/core/update_positions.cpp
    src/core/sort_particles.cpp
    src/core/update_electric_field.cpp
    src/core/update_velocities.cpp
    src/core/compute_energy.cpp
    src/core/save_positions.cpp
)

set(UTILS_SOURCES
    src/utils/utils.cpp
)

set(MAIN_SOURCES
    src/main_parallel.cpp
)

# Create executable
add_executable(sparc_parallel ${CORE_SOURCES} ${UTILS_SOURCES} ${MAIN_SOURCES})

# Link libraries
target_link_libraries(sparc_parallel OpenMP::OpenMP_CXX m)