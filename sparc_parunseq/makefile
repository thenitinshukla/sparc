# Makefile for SPARC ParUnseq Implementation

# Compiler and flags
CXX = g++

# Intel oneAPI TBB installation root
TBB_ROOT = /leonardo/prod/spack/06/install/0.22/linux-rhel8-icelake/gcc-8.5.0/intel-oneapi-tbb-2021.12.0-w4a57mvfeegdx4kymfajl5aio3kfhnnq/tbb/2021.12

# Compiler and linker flags
CXXFLAGS = -O3 -Wall -std=c++17 -Iinclude -I$(TBB_ROOT)/include -DTBB_PREVIEW_CONCURRENT_ORDERED_CONTAINERS=1
LDFLAGS = -L$(TBB_ROOT)/lib -ltbb -lm -pthread

# Check if TBB is available (optional)
ifeq ($(TBB_AVAILABLE), 1)
    CXXFLAGS += -ltbb
endif

# Source and object files
SRC_DIR = src
CORE_DIR = src/core
UTILS_DIR = src/utils
VISUALIZATION_DIR = src/visualization

SRCS = $(SRC_DIR)/main.cpp \
       $(CORE_DIR)/ParticleSystem.cpp \
       $(CORE_DIR)/compute_energy.cpp \
       $(CORE_DIR)/sort_particles.cpp \
       $(CORE_DIR)/update_electric_field.cpp \
       $(CORE_DIR)/update_positions.cpp \
       $(CORE_DIR)/performance.cpp \
       $(CORE_DIR)/save_positions.cpp \
       $(UTILS_DIR)/utils.cpp

OBJS = $(SRCS:.cpp=.o)

# Executable
EXEC = sparc_parunseq

# Default target: build the executable
all: $(EXEC)

# Rule to build the executable
$(EXEC): $(OBJS)
	$(CXX) $(OBJS) -o $(EXEC) $(LDFLAGS)

# Rule to build object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean up build artifacts
clean:
	rm -f $(OBJS) $(EXEC)

# Phony targets
.PHONY: all clean
