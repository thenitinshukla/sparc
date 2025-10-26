cmake_minimum_required(VERSION 3.10)
project(SPARC_CPP VERSION 1.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -Wall")

# Include directories
include_directories(include)

# Source files
set(CORE_SOURCES
    src/core/ParticleSystem.cpp
    src/core/compute_energy.cpp
    src/core/sort_particles.cpp
    src/core/update_electric_field.cpp
    src/core/update_positions.cpp
    src/core/performance.cpp
    src/core/save_positions.cpp
)

set(UTILS_SOURCES
    src/utils/utils.cpp
)

set(VISUALIZATION_SOURCES
    # Add visualization source files here when created
)

# All sources
set(SOURCES
    ${CORE_SOURCES}
    ${UTILS_SOURCES}
    ${VISUALIZATION_SOURCES}
    src/main.cpp
)

# Create executable
add_executable(sparc_cpp ${SOURCES})

# Link math library
target_link_libraries(sparc_cpp m)

# Set output directories
set_target_properties(sparc_cpp PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
)