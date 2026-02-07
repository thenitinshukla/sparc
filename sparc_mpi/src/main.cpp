/* ===============================================================
 * SPARC-MPI: Simulation of Particles in A Radial Configuration
 * MPI Parallelized Version
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
#include <mpi.h>

#ifdef _WIN32
#include <direct.h>
#else
#include <sys/stat.h>
#endif

#include "../include/ParticleSystem.h"

// Global configuration
int SAVE_INTERVAL = 100;
int MAX_SPECIES = 10;
int BUFFER_SIZE = 32768;

// Random number generator (seeded per rank for parallel initialization)
double randDouble() {
    return (double)rand() / RAND_MAX;
}

// Function to save species data (only rank 0 writes)
void saveSpeciesData(const std::string& filename, double time, double energy,
                     const ParticleSystem& system, double max_r2, const MPIContext& mpi) {
    if (mpi.rank != 0) return;

    std::ofstream file;
    if (time == 0.0) {
        file.open(filename);
        file << "Time(s),   Energy,   MaxR2,  NumParticles,  MPI_Ranks\n";
    } else {
        file.open(filename, std::ios::app);
    }

    if (file.is_open()) {
        file << std::fixed << std::setprecision(6) << time << ", " 
             << std::scientific << energy << ", " 
             << std::scientific << max_r2 << ", " 
             << system.n_total << ", "
             << mpi.size << "\n";
        file.close();
    }
}

int main(int argc, char* argv[]) {
    // Initialize MPI
    MPI_Init(&argc, &argv);

    MPIContext mpi;
    mpi.comm = MPI_COMM_WORLD;
    MPI_Comm_rank(mpi.comm, &mpi.rank);
    MPI_Comm_size(mpi.comm, &mpi.size);

    if (argc < 2) {
        if (mpi.rank == 0) {
            std::cout << "Usage: " << argv[0] << " <input_file> [-p] [-s] [-e] [-n]\n";
            std::cout << "Options:\n";
            std::cout << "  -p  Save particle positions\n";
            std::cout << "  -s  Save simulation data\n";
            std::cout << "  -e  Save energy distribution\n";
            std::cout << "  -n  Do not save any data\n";
        }
        MPI_Finalize();
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

    // Create output directory (rank 0 only)
    if (mpi.rank == 0 && (save_positions_flag || save_simulation_data_flag)) {
        #ifdef _WIN32
        _mkdir("output");
        #else
        mkdir("output", 0777);
        #endif
    }
    MPI_Barrier(mpi.comm);

    // Read input parameters from file (all ranks read to avoid broadcast overhead for small data)
    std::ifstream input_file(argv[1]);
    if (!input_file.is_open()) {
        if (mpi.rank == 0) {
            std::cout << "Error opening input file " << argv[1] << "\n";
        }
        MPI_Finalize();
        return 1;
    }

    long long N = 0;
    double R = 0, dt = 0, tend = 0;
    std::string line;
    std::vector<std::string> particle_names;
    std::vector<double> iqom_values;

    // Parse input file
    while (std::getline(input_file, line)) {
        if (line.empty() || line[0] == '#') continue;
        
        size_t start = line.find_first_not_of(" \t");
        if (start == std::string::npos) continue;
        std::string trimmed = line.substr(start);
        
        if (trimmed.substr(0, 2) == "N " || trimmed.substr(0, 2) == "N=") {
            size_t pos = line.find("=");
            if (pos != std::string::npos) {
                N = std::stoll(line.substr(pos + 1));
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
                particle_names.push_back(name);
                iqom_values.push_back(iqom);
            }
        }
    }
    input_file.close();

    int num_species = (int)particle_names.size();

    if (N == 0 || R == 0 || dt == 0 || tend == 0 || num_species == 0) {
        if (mpi.rank == 0) {
            std::cout << "Error: Missing or invalid parameters\n";
        }
        MPI_Finalize();
        return 1;
    }

    // Seed random number generator differently for each rank
    srand(10 + mpi.rank * 12345);

    const int Nt = (int)ceil(tend / dt);

    // Calculate particles per rank (distribute evenly)
    long long particles_per_rank = N / mpi.size;
    long long remainder = N % mpi.size;
    int local_N = (int)(particles_per_rank + (mpi.rank < remainder ? 1 : 0));

    if (mpi.rank == 0) {
        std::cout << "=== SPARC-MPI Simulation ===" << std::endl;
        std::cout << "Total particles: " << N << std::endl;
        std::cout << "MPI ranks: " << mpi.size << std::endl;
        std::cout << "Particles per rank (approx): " << particles_per_rank << std::endl;
        std::cout << "Time steps: " << Nt << std::endl;
        std::cout << "Species: " << num_species << std::endl;
        std::cout << "============================\n" << std::endl;
    }

    auto start_time = std::chrono::high_resolution_clock::now();

    // Initialize particle systems
    std::vector<std::unique_ptr<ParticleSystem>> particle_systems(num_species);
    std::vector<double> initial_energies(num_species, 0.0);
    double total_initial_energy = 0.0;
    double max_r2_global = 0.0;
    const double Q = 4.0 / 3.0 * 3.14159265358979323846 * R * R * R;

    // Create output filenames for each species
    std::vector<std::string> output_files(num_species);
    for (int i = 0; i < num_species; i++) {
        output_files[i] = "output/simulation_output_" + particle_names[i] + ".txt";
    }

    // Initialize particle systems with parallel particle generation
    for (int i = 0; i < num_species; i++) {
        particle_systems[i].reset(new ParticleSystem(local_N, N, particle_names[i], iqom_values[i]));
        
        int valid_particles = 0;
        double local_max_r2 = 0.0;

        // Each rank generates its own particles inside the sphere
        while (valid_particles < local_N) {
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
                particle_systems[i]->r2[valid_particles] = r2;

                if (r2 > local_max_r2) {
                    local_max_r2 = r2;
                }
                valid_particles++;
            }
        }

        // Get global max r^2
        double global_max_r2;
        MPI_Allreduce(&local_max_r2, &global_max_r2, 1, MPI_DOUBLE, MPI_MAX, mpi.comm);
        if (global_max_r2 > max_r2_global) {
            max_r2_global = global_max_r2;
        }

        // Initial sort to distribute particles by radius
        sortParticlesParallel(*particle_systems[i], mpi);
        updateElectricFieldParallel(*particle_systems[i], mpi);

        // Calculate initial energy
        initial_energies[i] = computeEnergyParallel(*particle_systems[i], mpi);
        total_initial_energy += initial_energies[i];

        if (save_simulation_data_flag) {
            saveSpeciesData(output_files[i], 0.0, initial_energies[i], 
                           *particle_systems[i], max_r2_global, mpi);
        }
    }

    // Print initial conditions
    if (mpi.rank == 0) {
        std::cout << "Initial Maximum r2 value: " << std::scientific << max_r2_global << "\n";
        std::cout << "Initial energy: " << std::scientific << total_initial_energy << "\n\n";
    }

    // Main simulation loop
    for (int it = 0; it < Nt; it++) {
        double total_current_energy = 0.0;

        for (int i = 0; i < num_species; i++) {
            ParticleSystem& ps = *particle_systems[i];
            
            // Sort and redistribute particles across ranks
            sortParticlesParallel(ps, mpi);
            
            // Compute electric field with distributed prefix sum
            updateElectricFieldParallel(ps, mpi);
            
            // Update positions (local computation)
            updatePositions(ps, dt);

            // Save particle positions if flag is set
            if (save_positions_flag && it % SAVE_INTERVAL == 0) {
                std::string pos_filename = "output/positions_" + particle_names[i] + 
                                          "_step_" + std::to_string(it) + ".bin";
                saveParticlePositions(pos_filename, ps, it, mpi);
            }

            if (it % SAVE_INTERVAL == 0) {
                double current_energy = computeEnergyParallel(ps, mpi);
                total_current_energy += current_energy;

                if (save_simulation_data_flag) {
                    double local_max_r2 = ps.getMaxRadiusSquared();
                    double global_max_r2;
                    MPI_Allreduce(&local_max_r2, &global_max_r2, 1, MPI_DOUBLE, MPI_MAX, mpi.comm);

                    saveSpeciesData(output_files[i], it * dt, current_energy, 
                                   ps, global_max_r2, mpi);
                }
            }
        }

        // Print energy conservation error at specified intervals (rank 0 only)
        if (it % SAVE_INTERVAL == 0 && mpi.rank == 0) {
            double energy_error = std::abs(total_current_energy - total_initial_energy) / 
                                total_initial_energy * 100;
            std::cout << "Step " << std::setw(6) << it 
                      << " | Time " << std::fixed << std::setprecision(4) << it * dt 
                      << " | Energy error: " << std::fixed << std::setprecision(6) 
                      << energy_error << "%\n";
        }
    }

    // Get final timing
    auto end_time = std::chrono::high_resolution_clock::now();
    double total_time = std::chrono::duration<double>(end_time - start_time).count();

    // Synchronize before printing summary
    MPI_Barrier(mpi.comm);

    // Print performance summary
    PerformanceMetricsSummary perf_metrics = calculatePerformanceMetrics(Nt, N, num_species, total_time);
    printPerformanceSummary(perf_metrics, mpi);

    MPI_Finalize();
    return 0;
}
