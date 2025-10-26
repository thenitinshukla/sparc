# Makefile for SPARC C++ version

# Compiler and flags
CXX = g++
CXXFLAGS = -O2 -g -Wall -std=c++11 -Iinclude
LDFLAGS = -lm

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
EXEC = sparc_cpp

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
