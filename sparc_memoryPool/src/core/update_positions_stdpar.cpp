#include "../../include/ParticleSystemStdPar.h"
#include <cmath>

void updatePositions(ParticleSystemStdPar& ps, double dt) {
    double* r = new double[ps.n_particles];
    double qom = 1.0 / ps.iqom;

    for (int i = 0; i < ps.n_particles; i++) {
        r[i] = std::sqrt(ps.x[i] * ps.x[i] + ps.y[i] * ps.y[i] + ps.z[i] * ps.z[i]);
    }

    for (int i = 0; i < ps.n_particles; i++) {
        // Update velocities
        ps.vx[i] += dt * qom * ps.Er[i] * ps.x[i] / r[i];
        ps.vy[i] += dt * qom * ps.Er[i] * ps.y[i] / r[i];
        ps.vz[i] += dt * qom * ps.Er[i] * ps.z[i] / r[i];

        // Update positions
        ps.x[i] += dt * ps.vx[i];
        ps.y[i] += dt * ps.vy[i];
        ps.z[i] += dt * ps.vz[i];
    }
    
    delete[] r;
}