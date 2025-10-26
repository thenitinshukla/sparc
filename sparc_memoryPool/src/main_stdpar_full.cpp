/* ===============================================================
 * SPARC: Simulation of Particles in A Radial Configuration (C++ stdpar version)
 * Adapted to use ParticleSystemStdPar with memory pool allocator
 * =============================================================== */

#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <chrono>
#include <iomanip>
#include <sstream>
#ifdef _WIN32
#include <direct.h>
#else
#include <sys/stat.h>
#endif

#include "../include/ParticleSystemStdPar.h"

// Forward declarations for our stdpar functions
void sortParticlesStdPar(ParticleSystemStdPar& ps);
void updateElectricFieldStdPar(ParticleSystemStdPar& ps);
void saveParticlePositions(const char* filename, const ParticleSystemStdPar& ps, int step);
double computeEnergy(const ParticleSystemStdPar& ps);
void updatePositions(ParticleSystemStdPar& ps, double dt);
double randDouble(); // Defined in utils.o

// For saving output
int SAVE_INTERVAL = 100;
int MAX_SPECIES = 10;
int BUFFER_SIZE = 32768;

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

    // Parse command-line options
    for (int i = 2; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "-p") save_positions_flag = 1;
        else if (arg == "-s") save_simulation_data_flag = 1;
        else if (arg == "-n") {
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
        
        // Parse parameters
        if (line.find("N") != std::string::npos && line.find("=") != std::string::npos) {
            size_t pos = line.find("=");
            N = std::stoi(line.substr(pos + 1));
        }
        else if (line.find("R") != std::string::npos && line.find("=") != std::string::npos) {
            size_t pos = line.find("=");
            R = std::stod(line.substr(pos + 1));
        }
        else if (line.find("dt") != std::string::npos && line.find("=") != std::string::npos) {
            size_t pos = line.find("=");
            dt = std::stod(line.substr(pos + 1));
        }
        else if (line.find("tend") != std::string::npos && line.find("=") != std::string::npos) {
            size_t pos = line.find("=");
            tend = std::stod(line.substr(pos + 1));
        }
        else if (line.find("SAVE_INTERVAL") != std::string::npos && line.find("=") != std::string::npos) {
            size_t pos = line.find("=");
            SAVE_INTERVAL = std::stoi(line.substr(pos + 1));
        }
        else if (line.find("MAX_SPECIES") != std::string::npos && line.find("=") != std::string::npos) {
            size_t pos = line.find("=");
            MAX_SPECIES = std::stoi(line.substr(pos + 1));
            // Reallocate arrays with new MAX_SPECIES value
            delete[] particle_names;
            delete[] iqom_values;
            particle_names = new std::string[MAX_SPECIES];
            iqom_values = new double[MAX_SPECIES];
        }
        else if (line.find("BUFFER_SIZE") != std::string::npos && line.find("=") != std::string::npos) {
            size_t pos = line.find("=");
            BUFFER_SIZE = std::stoi(line.substr(pos + 1));
        }
        else if (line.find("species") != std::string::npos) {
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

    // Initialize timing
    auto start_time = std::chrono::high_resolution_clock::now();
    double start_seconds = std::chrono::duration_cast<std::chrono::microseconds>(
        start_time.time_since_epoch()).count() / 1e6;

    // Initialize particle systems
    ParticleSystemStdPar** particle_systems = new ParticleSystemStdPar*[num_species];
    double* initial_energies = new double[num_species];
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
        particle_systems[i] = new ParticleSystemStdPar(N, particle_names[i].c_str(), iqom_values[i]);
        
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
            // Simple save function for now
            std::ofstream file(output_files[i]);
            if (file.is_open()) {
                file << "Time(s),   Energy,   MaxR2,  NumParticles\n";
                file << std::fixed << std::setprecision(6) << 0.0 << ", " 
                     << std::scientific << initial_energies[i] << ", " 
                     << std::scientific << max_r2_initial << ", " 
                     << particle_systems[i]->n_particles << "\n";
                file.close();
            }
        }
    }

    // Print initial conditions
    std::cout << "Initial Maximum r2 value: " << std::scientific << max_r2_global << "\n";
    std::cout << "Initial energy: " << std::scientific << total_initial_energy << "\n";

    // Main simulation loop
    for (int it = 0; it < Nt; it++) {
        double total_current_energy = 0.0;

        for (int i = 0; i < num_species; i++) {
            ParticleSystemStdPar& ps = *particle_systems[i];
            sortParticlesStdPar(ps);
            updateElectricFieldStdPar(ps);
            updatePositions(ps, dt);

            // Save particle positions if flag is set
            if (save_positions_flag && it % SAVE_INTERVAL == 0) {
                std::string pos_filename = "output/positions_" + particle_names[i] + "_step_" + std::to_string(it) + ".bin";
                saveParticlePositions(pos_filename.c_str(), ps, it);
            }

            if (it % SAVE_INTERVAL == 0) {
                double current_energy = computeEnergy(ps);
                total_current_energy += current_energy;

                if (save_simulation_data_flag) {
                    double max_r2 = 0.0;
                    for (int j = 0; j < ps.n_particles; j++) {
                        double r2 = ps.x[j] * ps.x[j] + ps.y[j] * ps.y[j] + ps.z[j] * ps.z[j];
                        if (r2 > max_r2) max_r2 = r2;
                    }

                    // Append to output file
                    std::ofstream file(output_files[i], std::ios::app);
                    if (file.is_open()) {
                        file << std::fixed << std::setprecision(6) << it * dt << ", " 
                             << std::scientific << current_energy << ", " 
                             << std::scientific << max_r2 << ", " 
                             << ps.n_particles << "\n";
                        file.close();
                    }
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

    // Print simple performance summary
    std::cout << "\nSimulation completed in " << std::fixed << std::setprecision(3) << total_time << " seconds\n";
    std::cout << "Total iterations: " << Nt << "\n";
    std::cout << "Particles per species: " << N << "\n";
    std::cout << "Number of species: " << num_species << "\n";

    // Clean up dynamically allocated memory
    for (int i = 0; i < num_species; i++) {
        delete particle_systems[i];
    }
    delete[] particle_systems;
    delete[] initial_energies;
    delete[] particle_names;
    delete[] iqom_values;
    delete[] output_files;

    return 0;
}