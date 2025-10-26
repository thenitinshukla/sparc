#include "../../include/ParticleSystem.h"
#include <algorithm>
#include <cmath>

// Constructor
ParticleSystem::ParticleSystem(int max_particles, const std::string& species_name, double inv_qom)
    : name(species_name), iqom(inv_qom), n_particles(max_particles) {
    // Resize all vectors to hold max_particles elements
    x.resize(max_particles);
    y.resize(max_particles);
    z.resize(max_particles);
    vx.resize(max_particles, 0.0);  // Initialize velocities to 0
    vy.resize(max_particles, 0.0);
    vz.resize(max_particles, 0.0);
    q.resize(max_particles);
    Er.resize(max_particles);
}

// Compute square of radius for all particles
std::vector<double> ParticleSystem::computeSquareRadius() const {
    std::vector<double> r2(n_particles);
    for (int i = 0; i < n_particles; i++) {
        r2[i] = x[i] * x[i] + y[i] * y[i] + z[i] * z[i];
    }
    return r2;
}

// Get maximum radius squared
double ParticleSystem::getMaxRadiusSquared() const {
    double max_r2 = 0.0;
    for (int i = 0; i < n_particles; i++) {
        double r2 = x[i] * x[i] + y[i] * y[i] + z[i] * z[i];
        if (r2 > max_r2) {
            max_r2 = r2;
        }
    }
    return max_r2;
}