#include "../../include/ParticleSystem.h"
#include <cmath>
#include <cstdlib>

double computeEnergy(const ParticleSystem& ps) {
    double K = 0;  // Kinetic energy
    double U = 0;  // Potential energy

    // Compute kinetic energy
    for (int i = 0; i < ps.n_particles; i++) {
        double v2 = ps.vx[i] * ps.vx[i] + ps.vy[i] * ps.vy[i] + ps.vz[i] * ps.vz[i];
        K += 0.5 * std::abs(ps.iqom * ps.q[i]) * v2;
    }

    // Compute potential energy
    for (int j = 0; j < ps.n_particles; j++) {
        for (int i = 0; i < ps.n_particles; i++) {
            if (i != j) {
                double rij = std::sqrt(std::pow(ps.x[i] - ps.x[j], 2) +
                                     std::pow(ps.y[i] - ps.y[j], 2) +
                                     std::pow(ps.z[i] - ps.z[j], 2));
                U += 0.5 * ps.q[i] * ps.q[j] / rij;
            }
        }
    }

    return K + U;
}