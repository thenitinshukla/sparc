cmake_minimum_required(VERSION 3.10)
project(SPARC_MPI LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find MPI
find_package(MPI REQUIRED)

# Optimization flags
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -Wall -Wextra")

# Default to Release build
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Source files
set(SOURCES
    src/main.cpp
    src/core/ParticleSystem.cpp
    src/core/sort_particles.cpp
    src/core/update_electric_field.cpp
    src/core/update_positions.cpp
    src/core/compute_energy.cpp
    src/core/performance.cpp
    src/core/save_positions.cpp
)

# Include directories
include_directories(include)
include_directories(${MPI_CXX_INCLUDE_DIRS})

# Create executable
add_executable(sparc_mpi ${SOURCES})

# Link MPI
target_link_libraries(sparc_mpi ${MPI_CXX_LIBRARIES})

# Set MPI compile flags
target_compile_options(sparc_mpi PRIVATE ${MPI_CXX_COMPILE_FLAGS})

# Installation
install(TARGETS sparc_mpi DESTINATION bin)

# Print configuration
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "MPI CXX compiler: ${MPI_CXX_COMPILER}")
message(STATUS "MPI include dirs: ${MPI_CXX_INCLUDE_DIRS}")
