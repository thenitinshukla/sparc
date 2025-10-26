#include "../include/ParticleSystemParallel.h"
#include <iostream>
#include <chrono>
#include <cmath>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <memory>

// Define M_PI if not available
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Function to parse input file
struct SimulationParameters {
    int N = 1000;           // Number of particles
    double R = 1.0;         // Radius of the sphere
    double dt = 0.01;       // Time step
    double tend = 0.1;      // End time
    int SAVE_INTERVAL = 10; // Save data every N steps
    int MAX_SPECIES = 2;    // Maximum number of particle species
    int BUFFER_SIZE = 32768; // Buffer size for file I/O
    std::string species_name = "electron";
    double species_mass = 1.0;
};

SimulationParameters parseInputFile(const std::string& filename) {
    SimulationParameters params;
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Warning: Could not open input file " << filename << ". Using default parameters.\n";
        return params;
    }
    
    std::string line;
    while (std::getline(file, line)) {
        // Skip comments and empty lines
        if (line.empty() || line[0] == '#') continue;
        
        // Find the '=' character
        size_t eq_pos = line.find('=');
        if (eq_pos != std::string::npos) {
            // Extract key and value
            std::string key = line.substr(0, eq_pos);
            std::string value = line.substr(eq_pos + 1);
            
            // Trim whitespace
            key.erase(0, key.find_first_not_of(" \t"));
            key.erase(key.find_last_not_of(" \t") + 1);
            value.erase(0, value.find_first_not_of(" \t"));
            value.erase(value.find_last_not_of(" \t") + 1);
            
            // Parse based on key
            if (key == "N") {
                params.N = std::stoi(value);
            } else if (key == "R") {
                params.R = std::stod(value);
            } else if (key == "dt") {
                params.dt = std::stod(value);
            } else if (key == "tend") {
                params.tend = std::stod(value);
            } else if (key == "SAVE_INTERVAL") {
                params.SAVE_INTERVAL = std::stoi(value);
            } else if (key == "MAX_SPECIES") {
                params.MAX_SPECIES = std::stoi(value);
            } else if (key == "BUFFER_SIZE") {
                params.BUFFER_SIZE = std::stoi(value);
            }
        } else if (line.find("species") == 0) {
            // Parse species line
            std::istringstream iss(line);
            std::string species_keyword;
            iss >> species_keyword >> params.species_name >> params.species_mass;
        }
    }
    
    file.close();
    return params;
}

// Simple random number generator (linear congruential generator)
double randDouble() {
    static unsigned int seed = 12345;
    seed = (1103515245 * seed + 12345) & 0x7fffffff;
    return static_cast<double>(seed) / static_cast<double>(0x7fffffff);
}

int main(int argc, char* argv[]) {
    std::string input_filename = "input.txt";
    if (argc > 1) {
        input_filename = argv[1];
    }
    
    // Parse input file
    SimulationParameters params = parseInputFile(input_filename);
    
    // Calculate number of time steps
    int Nt = static_cast<int>(params.tend / params.dt);
    
    std::cout << "SPARC Parallel Implementation\n";
    std::cout << "=============================\n";
    std::cout << "Input file: " << input_filename << "\n";
    std::cout << "Number of particles: " << params.N << "\n";
    std::cout << "Sphere radius: " << params.R << "\n";
    std::cout << "Time step size: " << params.dt << "\n";
    std::cout << "End time: " << params.tend << "\n";
    std::cout << "Number of time steps: " << Nt << "\n";
    std::cout << "Species: " << params.species_name << " (mass: " << params.species_mass << ")\n\n";
    
    // Total charge for uniform distribution
    const double Q = 4.0 / 3.0 * M_PI * params.R * params.R * params.R;
    
    // Create particle system
    ParticleSystemParallel ps(params.N, params.species_name.c_str(), params.species_mass);
    
    // Initialize particles with positions uniformly in sphere and zero velocities
    int valid_particles = 0;
    int attempts = 0;
    const int max_attempts = params.N * 100;
    
    while (valid_particles < params.N && attempts < max_attempts) {
        double x = -params.R + 2 * params.R * randDouble();
        double y = -params.R + 2 * params.R * randDouble();
        double z = -params.R + 2 * params.R * randDouble();
        double r2 = x * x + y * y + z * z;
        
        if (r2 <= params.R * params.R) {
            ps.x[valid_particles] = x;
            ps.y[valid_particles] = y;
            ps.z[valid_particles] = z;
            ps.vx[valid_particles] = 0.0;
            ps.vy[valid_particles] = 0.0;
            ps.vz[valid_particles] = 0.0;
            ps.q[valid_particles] = Q / params.N; // Uniform charge distribution
            
            valid_particles++;
        }
        attempts++;
    }
    
    std::cout << "Particles initialized\n";
    
    // Initial sorting
    std::cout << "Sorting particles initially\n";
    sortParticles(ps);
    std::cout << "Initial sorting completed\n";
    
    // Compute initial energy
    double initial_energy = computeEnergy(ps);
    std::cout << "Initial energy: " << std::scientific << std::setprecision(6) << initial_energy << "\n";
    
    // Time evolution loop
    auto start_time = std::chrono::high_resolution_clock::now();
    
    for (int step = 0; step < Nt; step++) {
        // Sort particles
        sortParticles(ps);
        
        // Update electric field
        updateElectricField(ps);
        
        // Update velocities based on electric field
        updateVelocities(ps, params.dt);
        
        // Update positions
        updatePositions(ps, params.dt);
        
        // Print energy conservation error at regular intervals
        if (step % params.SAVE_INTERVAL == 0) {
            double current_energy = computeEnergy(ps);
            double energy_error = std::abs((current_energy - initial_energy) / initial_energy) * 100.0;
            double current_time = step * params.dt;
            std::cout << "At time " << std::fixed << std::setprecision(1) << current_time 
                      << ", energy conservation error: " << std::fixed << std::setprecision(6) 
                      << energy_error << "%\n";
        }
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();
    
    // Final sorting
    std::cout << "Final sorting\n";
    sortParticles(ps);
    
    // Compute final energy
    double final_energy = computeEnergy(ps);
    std::cout << "Final energy: " << std::scientific << std::setprecision(6) << final_energy << "\n";
    
    // Save final state
    saveParticlePositions("final_positions_parallel.txt", ps, Nt);
    
    std::cout << "\nSimulation completed successfully!\n";
    std::cout << "Execution time: " << duration << " ms\n";
    
    return 0;
}