# Makefile for SPARC Parallel Implementation

# Compiler and flags
CXX = g++
CXXFLAGS = -O3 -Wall -std=c++17 -fopenmp
INCLUDES = -Iinclude
LIBS = -lm -ltbb

# Source files
CORE_SRC = src/core/ParticleSystemParallel.cpp src/core/update_positions.cpp src/core/sort_particles.cpp \
           src/core/update_electric_field.cpp src/core/update_velocities.cpp src/core/compute_energy.cpp \
           src/core/save_positions.cpp
UTILS_SRC = src/utils/utils.cpp
MAIN_SRC = src/main_parallel.cpp

# Object files
CORE_OBJ = $(CORE_SRC:.cpp=.o)
UTILS_OBJ = $(UTILS_SRC:.cpp=.o)
MAIN_OBJ = $(MAIN_SRC:.cpp=.o)

# Executable
EXECUTABLE = sparc_parallel

# Default target
all: $(EXECUTABLE)

# Link executable
$(EXECUTABLE): $(CORE_OBJ) $(UTILS_OBJ) $(MAIN_OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LIBS)

# Compile core files
src/core/%.o: src/core/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Compile utils files
src/utils/%.o: src/utils/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Compile main file
src/%.o: src/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Clean build files
clean:
	rm -f $(CORE_OBJ) $(UTILS_OBJ) $(MAIN_OBJ) $(EXECUTABLE)

# Rebuild everything
rebuild: clean all

.PHONY: all clean rebuild
