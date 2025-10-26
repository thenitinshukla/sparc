#include "../../include/ParticleSystem.h"
#include <algorithm>
#include <cmath>

void sortParticles(ParticleSystem& ps) {
    std::vector<double> r2 = ps.computeSquareRadius();

    // Simple bubble sort (can be optimized with better sorting algorithm)
    for (int i = 0; i < ps.n_particles - 1; i++) {
        for (int j = 0; j < ps.n_particles - i - 1; j++) {
            if (r2[j] > r2[j + 1]) {
                // Swap all particle properties
                std::swap(r2[j], r2[j + 1]);
                std::swap(ps.x[j], ps.x[j + 1]);
                std::swap(ps.y[j], ps.y[j + 1]);
                std::swap(ps.z[j], ps.z[j + 1]);
                std::swap(ps.vx[j], ps.vx[j + 1]);
                std::swap(ps.vy[j], ps.vy[j + 1]);
                std::swap(ps.vz[j], ps.vz[j + 1]);
                std::swap(ps.q[j], ps.q[j + 1]);
                std::swap(ps.Er[j], ps.Er[j + 1]);
            }
        }
    }
}