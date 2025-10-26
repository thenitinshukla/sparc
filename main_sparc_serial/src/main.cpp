/* ===============================================================
 * SPARC: Simulation of Particles in A Radial Configuration (C++ version)
 * Created by Nitin Shukla, January 2025
 * Copyright (c) 2025 CINECA 
 * =============================================================== */

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <algorithm>
#include <chrono>
#include <iomanip>
#include <sstream>
#ifdef _WIN32
#include <direct.h>
#else
#include <sys/stat.h>
#endif

#include "../include/ParticleSystem.h"

// For saving output
int SAVE_INTERVAL = 100;
int MAX_SPECIES = 10;
int BUFFER_SIZE = 32768;

// Function declarations
double randDouble();
void saveSpeciesData(const std::string& filename, double time, double energy,
                     const ParticleSystem& system, const PerformanceMetrics& metrics,
                     double max_r2);

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cout << "Usage: " << argv[0] << " <input_file> [-p] [-s] [-e] [-n]\n";
        std::cout << "Options:\n";
        std::cout << "  -p  Save particle positions\n";
        std::cout << "  -s  Save simulation data\n";
        std::cout << "  -e  Save energy distribution\n";
        std::cout << "  -n  Do not save any data\n";
        return 1;
    }

    // Flags to control what to save
    int save_positions_flag = 0;
    int save_simulation_data_flag = 1;
    int save_energy_distribution_flag = 0;
    int no_save_flag = 0;

    // Parse command-line options
    for (int i = 2; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "-p") save_positions_flag = 1;
        else if (arg == "-s") save_simulation_data_flag = 1;
        else if (arg == "-e") save_energy_distribution_flag = 1;
        else if (arg == "-n") {
            no_save_flag = 1;
            save_simulation_data_flag = 0;
        }
    }

    // Create output directory if saving data and it doesn't exist
    if (save_positions_flag || save_simulation_data_flag) {
        #ifdef _WIN32
        _mkdir("output");
        #else
        mkdir("output", 0777);
        #endif
    }

    // Read input parameters from file
    std::ifstream input_file(argv[1]);
    if (!input_file.is_open()) {
        std::cout << "Error opening input file " << argv[1] << "\n";
        return 1;
    }

    int N = 0;
    double R = 0, dt = 0, tend = 0;
    std::string line;
    std::string* particle_names = new std::string[MAX_SPECIES];
    double* iqom_values = new double[MAX_SPECIES];
    int num_species = 0;

    // Parse input file
    while (std::getline(input_file, line)) {
        // Skip comments and empty lines
        if (line.empty() || line[0] == '#') continue;
        
        // Trim leading whitespace for parsing
        size_t start = line.find_first_not_of(" \t");
        if (start == std::string::npos) continue;
        std::string trimmed = line.substr(start);
        
        // Parse parameters - check if line STARTS with the parameter name
        if (trimmed.substr(0, 2) == "N " || trimmed.substr(0, 2) == "N=") {
            size_t pos = line.find("=");
            if (pos != std::string::npos) {
                N = std::stoi(line.substr(pos + 1));
            }
        }
        else if (trimmed.substr(0, 2) == "R " || trimmed.substr(0, 2) == "R=") {
            size_t pos = line.find("=");
            if (pos != std::string::npos) {
                R = std::stod(line.substr(pos + 1));
            }
        }
        else if (trimmed.substr(0, 3) == "dt " || trimmed.substr(0, 3) == "dt=") {
            size_t pos = line.find("=");
            if (pos != std::string::npos) {
                dt = std::stod(line.substr(pos + 1));
            }
        }
        else if (trimmed.substr(0, 5) == "tend " || trimmed.substr(0, 5) == "tend=") {
            size_t pos = line.find("=");
            if (pos != std::string::npos) {
                tend = std::stod(line.substr(pos + 1));
            }
        }
        else if (trimmed.substr(0, 13) == "SAVE_INTERVAL") {
            size_t pos = line.find("=");
            if (pos != std::string::npos) {
                SAVE_INTERVAL = std::stoi(line.substr(pos + 1));
            }
        }
        else if (trimmed.substr(0, 11) == "MAX_SPECIES") {
            size_t pos = line.find("=");
            if (pos != std::string::npos) {
                MAX_SPECIES = std::stoi(line.substr(pos + 1));
                // Reallocate arrays with new MAX_SPECIES value
                delete[] particle_names;
                delete[] iqom_values;
                particle_names = new std::string[MAX_SPECIES];
                iqom_values = new double[MAX_SPECIES];
            }
        }
        else if (trimmed.substr(0, 11) == "BUFFER_SIZE") {
            size_t pos = line.find("=");
            if (pos != std::string::npos) {
                BUFFER_SIZE = std::stoi(line.substr(pos + 1));
            }
        }
        else if (trimmed.substr(0, 7) == "species") {
            std::istringstream iss(line);
            std::string species_keyword, name;
            double iqom;
            if (iss >> species_keyword >> name >> iqom) {
                if (num_species < MAX_SPECIES) {
                    particle_names[num_species] = name;
                    iqom_values[num_species] = iqom;
                    num_species++;
                } else {
                    std::cout << "Warning: Maximum number of species reached, ignoring " << name << "\n";
                }
            }
        }
    }
    input_file.close();

    if (N == 0 || R == 0 || dt == 0 || tend == 0 || num_species == 0) {
        std::cout << "Error: Missing or invalid parameters\n";
        return 1;
    }

    srand(10);
    const int Nt = (int)ceil(tend / dt);

    // Initialize performance metrics
    PerformanceMetrics metrics = {0};
    auto start_time = std::chrono::high_resolution_clock::now();
    double start_seconds = std::chrono::duration_cast<std::chrono::microseconds>(
        start_time.time_since_epoch()).count() / 1e6;

    // Initialize particle systems
    std::vector<std::unique_ptr<ParticleSystem>> particle_systems(num_species);
    std::vector<double> initial_energies(num_species, 0.0);
    double total_initial_energy = 0.0;
    double max_r2_global = 0.0;
    const double Q = 4.0 / 3.0 * 3.14159265358979323846 * R * R * R;

    // Create output filenames for each species
    std::string* output_files = new std::string[MAX_SPECIES];
    for (int i = 0; i < num_species; i++) {
        output_files[i] = "output/simulation_output_" + particle_names[i] + ".txt";
    }

    // Initialize particle systems and calculate initial conditions
    for (int i = 0; i < num_species; i++) {
        particle_systems[i].reset(new ParticleSystem(N, particle_names[i], iqom_values[i]));
        
        int valid_particles = 0;
        double max_r2_initial = 0.0;

        while (valid_particles < N) {
            double x = -R + 2 * R * randDouble();
            double y = -R + 2 * R * randDouble();
            double z = -R + 2 * R * randDouble();
            double r2 = x * x + y * y + z * z;

            if (r2 <= R * R) {
                particle_systems[i]->x[valid_particles] = x;
                particle_systems[i]->y[valid_particles] = y;
                particle_systems[i]->z[valid_particles] = z;
                particle_systems[i]->vx[valid_particles] = 0.0;
                particle_systems[i]->vy[valid_particles] = 0.0;
                particle_systems[i]->vz[valid_particles] = 0.0;
                particle_systems[i]->q[valid_particles] = Q / N;

                if (r2 > max_r2_initial) {
                    max_r2_initial = r2;
                }
                valid_particles++;
            }
        }

        if (max_r2_initial > max_r2_global) {
            max_r2_global = max_r2_initial;
        }

        // Calculate initial energy
        initial_energies[i] = computeEnergy(*particle_systems[i]);
        total_initial_energy += initial_energies[i];

        if (save_simulation_data_flag) {
            // update_performance_metrics(&metrics, particle_systems[i], start_seconds);
            saveSpeciesData(output_files[i], 0.0, initial_energies[i], 
                           *particle_systems[i], metrics, max_r2_initial);
        }
    }

    // Print initial conditions
    std::cout << "Initial Maximum r2 value: " << std::scientific << max_r2_global << "\n";
    std::cout << "Initial energy: " << std::scientific << total_initial_energy << "\n";

    // Main simulation loop
    for (int it = 0; it < Nt; it++) {
        double total_current_energy = 0.0;

        for (int i = 0; i < num_species; i++) {
            ParticleSystem& ps = *particle_systems[i];
            sortParticles(ps);
            updateElectricField(ps);
            updatePositions(ps, dt);

            // Save particle positions if flag is set
            if (save_positions_flag && it % SAVE_INTERVAL == 0) {
                std::string pos_filename = "output/positions_" + particle_names[i] + "_step_" + std::to_string(it) + ".bin";
                saveParticlePositions(pos_filename, ps, it);
            }

            if (it % SAVE_INTERVAL == 0) {
                double current_energy = computeEnergy(ps);
                total_current_energy += current_energy;

                if (save_simulation_data_flag) {
                    double max_r2 = ps.getMaxRadiusSquared();

                    // update_performance_metrics(&metrics, ps, start_seconds);
                    saveSpeciesData(output_files[i], it * dt, current_energy, 
                                   ps, metrics, max_r2);
                }
            }
        }

        // Print energy conservation error at specified intervals
        if (it % SAVE_INTERVAL == 0) {
            double energy_error = std::abs(total_current_energy - total_initial_energy) / 
                                total_initial_energy * 100;
            std::cout << "At time " << std::fixed << std::setprecision(1) << it * dt 
                      << ", energy conservation error: " << std::fixed << std::setprecision(6) 
                      << energy_error << "%\n";
        }
    }

    // Get final timing
    auto end_time = std::chrono::high_resolution_clock::now();
    double end_seconds = std::chrono::duration_cast<std::chrono::microseconds>(
        end_time.time_since_epoch()).count() / 1e6;
    double total_time = end_seconds - start_seconds;

    // Print performance summary
    PerformanceMetricsSummary perf_metrics = calculatePerformanceMetrics(Nt, N, num_species, total_time);
    printPerformanceSummary(perf_metrics);

    // Clean up dynamically allocated memory
    delete[] particle_names;
    delete[] iqom_values;
    delete[] output_files;

    return 0;
}

// Save simulation data for a specific species
void saveSpeciesData(const std::string& filename, double time, double energy,
                     const ParticleSystem& system, const PerformanceMetrics& metrics,
                     double max_r2) {
    std::ofstream file;
    if (time == 0.0) {
        file.open(filename);
        file << "Time(s),   Energy,   MaxR2,  NumParticles,  TotalExecutionTime(s),   Throughput(GFLOPS),  MemoryBandwidth(GB/s)\n";
    } else {
        file.open(filename, std::ios::app);
    }

    if (file.is_open()) {
        file << std::fixed << std::setprecision(6) << time << ", " 
             << std::scientific << energy << ", " 
             << std::scientific << max_r2 << ", " 
             << system.n_particles << ", " 
             << std::fixed << std::setprecision(6) << metrics.elapsed_time << ","
             << std::fixed << std::setprecision(3) << metrics.gflops << ","
             << std::fixed << std::setprecision(6) << metrics.bandwidth << "\n";
        file.close();
    }
}