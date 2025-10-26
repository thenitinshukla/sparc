#include "../../include/ParticleSystem.h"
#include <cmath>
#include <vector>
#include <execution>
#include <algorithm>
#include <numeric>

void updatePositions(ParticleSystem& ps, double dt) {
    const int n = ps.n_particles;
    const double qom = 1.0 / ps.iqom;
    
    // Compute radii using parallel unsequenced execution
    std::vector<double> r(n);
    std::vector<int> indices(n);
    std::iota(indices.begin(), indices.end(), 0);
    
    std::for_each(
        std::execution::par_unseq,
        indices.begin(), indices.end(),
        [&](int i) {
            r[i] = std::sqrt(ps.x[i] * ps.x[i] + ps.y[i] * ps.y[i] + ps.z[i] * ps.z[i]);
        }
    );
    
    // Update velocities using parallel unsequenced execution
    std::for_each(
        std::execution::par_unseq,
        indices.begin(), indices.end(),
        [&](int i) {
            double inv_r = 1.0 / r[i];
            double factor = dt * qom * ps.Er[i] * inv_r;
            
            ps.vx[i] += factor * ps.x[i];
            ps.vy[i] += factor * ps.y[i];
            ps.vz[i] += factor * ps.z[i];
        }
    );
    
    // Update positions using parallel unsequenced execution
    std::for_each(
        std::execution::par_unseq,
        indices.begin(), indices.end(),
        [&](int i) {
            ps.x[i] += dt * ps.vx[i];
            ps.y[i] += dt * ps.vy[i];
            ps.z[i] += dt * ps.vz[i];
        }
    );
}
