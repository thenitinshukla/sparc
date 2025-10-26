# Makefile for SPARC C++ stdpar version

# Compiler and flags
CXX = g++
CXXFLAGS = -O3 -Wall -std=c++17 -Iinclude -DTBB_PREVIEW_CONCURRENT_ORDERED_CONTAINERS=1
LDFLAGS = -lm

# Check if TBB is available
ifeq ($(TBB_AVAILABLE), 1)
    CXXFLAGS += -ltbb
endif

# Directories
SRC_DIR = src
CORE_DIR = $(SRC_DIR)/core
UTILS_DIR = $(SRC_DIR)/utils


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
EXEC = sparc_std

# Default target
all: $(EXEC)

# Link step
$(EXEC): $(OBJS)
	$(CXX) $(CXXFLAGS) $(OBJS) -o $@ $(LDFLAGS)

# Compile step
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean up
clean:
	rm -f $(OBJS) $(EXEC)

.PHONY: all clean

