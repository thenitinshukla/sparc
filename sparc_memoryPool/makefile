# Makefile for SPARC C++ stdpar version

# Compiler and flags
CXX = g++
CXXFLAGS = -O3 -Wall -std=c++17 -Iinclude -DTBB_PREVIEW_CONCURRENT_ORDERED_CONTAINERS=1
LDFLAGS = -lm

# Check if TBB is available
ifeq ($(TBB_AVAILABLE), 1)
    CXXFLAGS += -ltbb
endif

# Source and object files
SRC_DIR = src
CORE_DIR = src/core
UTILS_DIR = src/utils

# Stdpar full sources (only version we're keeping)
STDPAR_FULL_SRCS = $(SRC_DIR)/main_stdpar_full.cpp \
       $(CORE_DIR)/ParticleSystemStdPar.cpp \
       $(CORE_DIR)/compute_energy_stdpar.cpp \
       $(CORE_DIR)/sort_particles_stdpar.cpp \
       $(CORE_DIR)/update_electric_field_stdpar.cpp \
       $(CORE_DIR)/update_positions_stdpar.cpp \
       $(CORE_DIR)/save_positions_stdpar.cpp \
       $(UTILS_DIR)/utils.cpp

STDPAR_FULL_OBJS = $(STDPAR_FULL_SRCS:.cpp=.o)

# Executables
EXEC_STDPAR_FULL = sparc_mempool

# Default target: build stdpar full version
all: $(EXEC_STDPAR_FULL)

# Rule to build the stdpar full executable
$(EXEC_STDPAR_FULL): $(STDPAR_FULL_OBJS)
	$(CXX) $(CXXFLAGS) $(STDPAR_FULL_OBJS) -o $(EXEC_STDPAR_FULL) $(LDFLAGS)

# Rule to build object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean up build artifacts
clean:
	rm -f $(STDPAR_FULL_OBJS) $(EXEC_STDPAR_FULL)

# Phony targets
.PHONY: all clean
