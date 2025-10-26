#include "../../include/ParticleSystemStdPar.h"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <vector>

// Static memory pool allocator for all particle data
static MemoryPoolAllocator<double> particleAllocator(1024 * 1024 * sizeof(double)); // 1MB pool

// Constructor
ParticleSystemStdPar::ParticleSystemStdPar(int max_particles, const char* species_name, double inv_qom)
    : iqom(inv_qom), n_particles(max_particles) {
    // Copy the species name (simple implementation)
    int i = 0;
    while (species_name[i] != '\0' && i < sizeof(name) - 1) {
        name[i] = species_name[i];
        i++;
    }
    name[i] = '\0'; // Ensure null termination
    
    // Reserve space in vectors using our custom memory pool allocator
    x.reserve(max_particles);
    y.reserve(max_particles);
    z.reserve(max_particles);
    vx.reserve(max_particles);
    vy.reserve(max_particles);
    vz.reserve(max_particles);
    q.reserve(max_particles);
    Er.reserve(max_particles);
    
    // Resize vectors to hold max_particles elements
    x.resize(max_particles);
    y.resize(max_particles);
    z.resize(max_particles);
    vx.resize(max_particles);
    vy.resize(max_particles);
    vz.resize(max_particles);
    q.resize(max_particles);
    Er.resize(max_particles);
    
    // Initialize velocities to 0
    for (int i = 0; i < max_particles; i++) {
        vx[i] = 0.0;
        vy[i] = 0.0;
        vz[i] = 0.0;
    }
}

// Destructor
ParticleSystemStdPar::~ParticleSystemStdPar() {
    // Vectors will automatically deallocate using the custom allocator
}

// Compute square of radius for all particles
std::vector<double> ParticleSystemStdPar::computeSquareRadius() const {
    // Create vector with default allocator to avoid issues
    std::vector<double> r2(n_particles);
    for (int i = 0; i < n_particles; i++) {
        r2[i] = x[i] * x[i] + y[i] * y[i] + z[i] * z[i];
    }
    return r2;
}

// Get maximum radius squared
double ParticleSystemStdPar::getMaxRadiusSquared() const {
    double max_r2 = 0.0;
    for (int i = 0; i < n_particles; i++) {
        double r2 = x[i] * x[i] + y[i] * y[i] + z[i] * z[i];
        if (r2 > max_r2) {
            max_r2 = r2;
        }
    }
    return max_r2;
}