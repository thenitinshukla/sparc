#include "../../include/ParticleSystem.h"
#include <algorithm>
#include <cmath>

ParticleSystem::ParticleSystem(int local_particles, long long total_particles,
                               const std::string& species_name, double inv_qom)
    : name(species_name), iqom(inv_qom), n_particles(local_particles), n_total(total_particles) {
    resize(local_particles);
}

void ParticleSystem::resize(int new_size) {
    n_particles = new_size;
    x.resize(new_size);
    y.resize(new_size);
    z.resize(new_size);
    vx.resize(new_size);
    vy.resize(new_size);
    vz.resize(new_size);
    q.resize(new_size);
    Er.resize(new_size);
    r2.resize(new_size);
}

void ParticleSystem::computeSquareRadius() {
    for (int i = 0; i < n_particles; i++) {
        r2[i] = x[i] * x[i] + y[i] * y[i] + z[i] * z[i];
    }
}

double ParticleSystem::getMaxRadiusSquared() const {
    double max_r2 = 0.0;
    for (int i = 0; i < n_particles; i++) {
        if (r2[i] > max_r2) max_r2 = r2[i];
    }
    return max_r2;
}
