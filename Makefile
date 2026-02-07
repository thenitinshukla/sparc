# Compiler (use MPI wrapper)
CXX = mpic++

# Compiler flags
CXXFLAGS = -O3 -std=c++14 -Wall -march=native
DEBUG_FLAGS = -g -O0 -std=c++14 -Wall
FAST_FLAGS = -O3 -std=c++14 -Wall -march=native -DUSE_FAST_ENERGY=1

# Include directories
INCLUDES = -I./include

# Source files
SOURCES = src/main.cpp \
          src/core/ParticleSystem.cpp \
          src/core/sort_particles.cpp \
          src/core/update_electric_field.cpp \
          src/core/update_positions.cpp \
          src/core/compute_energy.cpp \
          src/core/performance.cpp \
          src/core/save_positions.cpp

# Object files
OBJECTS = $(SOURCES:.cpp=.o)

# Target executable
TARGET = sparc_mpi

# Default target - uses exact O(N^2) energy calculation for verification
all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(INCLUDES) -o $@ $(OBJECTS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Debug build
debug: CXXFLAGS = $(DEBUG_FLAGS)
debug: clean $(TARGET)

# Fast build - uses O(N) energy approximation for large-scale production runs
fast: CXXFLAGS = $(FAST_FLAGS)
fast: clean $(TARGET)
	@echo "Built with O(N) fast energy calculation"

# Clean
clean:
	rm -f $(OBJECTS) $(TARGET)

# Run with specified number of MPI processes
run: $(TARGET)
	mpirun -np 4 ./$(TARGET) input_file.txt

run2: $(TARGET)
	mpirun -np 2 ./$(TARGET) input_file.txt

run8: $(TARGET)
	mpirun -np 8 ./$(TARGET) input_file.txt

.PHONY: all clean debug fast run run2 run8

