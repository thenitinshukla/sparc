cmake_minimum_required(VERSION 3.12)
cmake_policy(SET CMP0074 NEW)
project(SPARC_PARUNSEQ VERSION 1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall -march=native")

# Find Intel TBB for parallel algorithms
find_package(TBB QUIET)

if (TBB_FOUND)
    message(STATUS "TBB found: ${TBB_INCLUDE_DIRS}")
    add_definitions(-DTBB_AVAILABLE=1)
else()
    message(WARNING "TBB not found. Some parallel features may not work.")
endif()

# Include directories
include_directories(include)
if (TBB_FOUND)
    include_directories(${TBB_INCLUDE_DIRS})
endif()

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
add_executable(sparc_parunseq ${SOURCES})

# Link libraries
target_link_libraries(sparc_parunseq PRIVATE m)

# Link TBB if found
if (TBB_FOUND)
    target_link_libraries(sparc_parunseq PRIVATE TBB::tbb)
endif()

# Set output directories
set_target_properties(sparc_parunseq PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
)