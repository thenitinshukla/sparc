cmake_minimum_required(VERSION 3.12)  # CMP0074 requires 3.12+
cmake_policy(SET CMP0074 NEW)

project(sparc_cpp_stdpar_full LANGUAGES CXX)

# ============================================================
# Compiler setup
# ============================================================
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall -DTBB_PREVIEW_CONCURRENT_ORDERED_CONTAINERS=1")

# ============================================================
# Find oneTBB (Intel Threading Building Blocks)
# ============================================================
find_package(TBB QUIET)

if (TBB_FOUND)
    message(STATUS "TBB found: ${TBB_INCLUDE_DIRS}")
    add_definitions(-DTBB_AVAILABLE=1)
else()
    message(WARNING "TBB not found, continuing without it.")
endif()

# ============================================================
# Include directories
# ============================================================
include_directories(include)
if (TBB_FOUND)
    include_directories(${TBB_INCLUDE_DIRS})
endif()

# ============================================================
# Source files
# ============================================================
set(SRC_DIR src)
set(CORE_DIR ${SRC_DIR}/core)
set(UTILS_DIR ${SRC_DIR}/utils)

set(STDPAR_FULL_SRCS
    ${SRC_DIR}/main_stdpar_full.cpp
    ${CORE_DIR}/ParticleSystemStdPar.cpp
    ${CORE_DIR}/compute_energy_stdpar.cpp
    ${CORE_DIR}/sort_particles_stdpar.cpp
    ${CORE_DIR}/update_electric_field_stdpar.cpp
    ${CORE_DIR}/update_positions_stdpar.cpp
    ${CORE_DIR}/save_positions_stdpar.cpp
    ${UTILS_DIR}/utils.cpp
)

# ============================================================
# Target
# ============================================================
add_executable(sparc_cpp_stdpar_full ${STDPAR_FULL_SRCS})

# Link math library
target_link_libraries(sparc_cpp_stdpar_full PRIVATE m)

# Link TBB if found
if (TBB_FOUND)
    target_link_libraries(sparc_cpp_stdpar_full PRIVATE TBB::tbb)
endif()

