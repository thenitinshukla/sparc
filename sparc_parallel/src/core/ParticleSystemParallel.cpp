#include "../../include/ParticleSystemParallel.h"
#include <vector>
#include <string>
#include <cmath>
#include <cstring>  // for strncpy

ParticleSystemParallel::ParticleSystemParallel(int max_particles, const char* species_name, double inv_qom) 
    : iqom(inv_qom), n_particles(max_particles) {
    // Initialize name
    std::strncpy(name, species_name, sizeof(name) - 1);
    name[sizeof(name) - 1] = '\0';  // Ensure null termination
    
    // Resize vectors to hold max_particles
    x.resize(max_particles);
    y.resize(max_particles);
    z.resize(max_particles);
    vx.resize(max_particles);
    vy.resize(max_particles);
    vz.resize(max_particles);
    q.resize(max_particles);
    Er.resize(max_particles);
}

ParticleSystemParallel::~ParticleSystemParallel() {
    // Destructor - vectors will automatically clean up
}

std::vector<double> ParticleSystemParallel::computeSquareRadius() const {
    std::vector<double> r2(n_particles);
    
    // Compute r^2 = x^2 + y^2 + z^2 for all particles
    for (int i = 0; i < n_particles; i++) {
        r2[i] = x[i] * x[i] + y[i] * y[i] + z[i] * z[i];
    }
    
    return r2;
}

double ParticleSystemParallel::getMaxRadiusSquared() const {
    std::vector<double> r2 = computeSquareRadius();
    double max_r2 = 0.0;
    
    for (int i = 0; i < n_particles; i++) {
        if (r2[i] > max_r2) {
            max_r2 = r2[i];
        }
    }
    
    return max_r2;
}