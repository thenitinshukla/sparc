#include "../../include/ParticleSystemStdPar.h"
#include <fstream>
#include <iostream>

void saveParticlePositions(const char* filename, const ParticleSystemStdPar& ps, int step) {
    std::ofstream file(filename, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Error opening file for saving particle positions: " << filename << std::endl;
        return;
    }
    
    // Write the time step
    file.write(reinterpret_cast<const char*>(&step), sizeof(int));
    
    // Write the number of particles
    file.write(reinterpret_cast<const char*>(&ps.n_particles), sizeof(int));
    
    // Write particle positions
    file.write(reinterpret_cast<const char*>(ps.x), ps.n_particles * sizeof(double));
    file.write(reinterpret_cast<const char*>(ps.y), ps.n_particles * sizeof(double));
    file.write(reinterpret_cast<const char*>(ps.z), ps.n_particles * sizeof(double));
    
    file.close();
}