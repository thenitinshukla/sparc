#include "../../include/ParticleSystemParallel.h"
#include <fstream>
#include <iostream>

void saveParticlePositions(const std::string& filename, const ParticleSystemParallel& ps, int step) {
    std::ofstream file(filename, std::ios::app);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << " for writing.\n";
        return;
    }
    
    file << "Step: " << step << "\n";
    file << "Particle data (x, y, z, vx, vy, vz):\n";
    
    for (int i = 0; i < ps.n_particles; i++) {
        file << ps.x[i] << " " << ps.y[i] << " " << ps.z[i] << " "
             << ps.vx[i] << " " << ps.vy[i] << " " << ps.vz[i] << "\n";
    }
    
    file << "\n";
    file.close();
}