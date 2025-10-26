#include "../../include/ParticleSystem.h"
#include <cmath>
#include <cstdlib>
#include <execution>
#include <algorithm>
#include <numeric>
#include <vector>

// Compute kinetic energy using parallel unsequenced execution
double computeKineticEnergy(const ParticleSystem& ps) {
    std::vector<int> indices(ps.n_particles);
    std::iota(indices.begin(), indices.end(), 0);
    
    double K = std::transform_reduce(
        std::execution::par_unseq,
        indices.begin(), indices.end(),
        0.0,  // Initial value
        std::plus<>(),  // Reduction operation
        [&ps](int i) {  // Transform operation
            double v2 = ps.vx[i] * ps.vx[i] + ps.vy[i] * ps.vy[i] + ps.vz[i] * ps.vz[i];
            return 0.5 * std::abs(ps.iqom * ps.q[i]) * v2;
        }
    );
    
    return K;
}

// Compute potential energy using parallel unsequenced execution
double computePotentialEnergy(const ParticleSystem& ps) {
    std::vector<int> indices(ps.n_particles);
    std::iota(indices.begin(), indices.end(), 0);
    
    double U = std::transform_reduce(
        std::execution::par_unseq,
        indices.begin(), indices.end(),
        0.0,  // Initial value
        std::plus<>(),  // Reduction operation
        [&ps](int j) {  // Transform operation for outer loop
            double U_j = 0.0;
            for (int i = 0; i < ps.n_particles; i++) {
                if (i != j) {
                    double dx = ps.x[i] - ps.x[j];
                    double dy = ps.y[i] - ps.y[j];
                    double dz = ps.z[i] - ps.z[j];
                    double rij = std::sqrt(dx * dx + dy * dy + dz * dz);
                    U_j += 0.5 * ps.q[i] * ps.q[j] / rij;
                }
            }
            return U_j;
        }
    );
    
    return U;
}

double computeEnergy(const ParticleSystem& ps) {
    double K = computeKineticEnergy(ps);
    double U = computePotentialEnergy(ps);
    return K + U;
}
