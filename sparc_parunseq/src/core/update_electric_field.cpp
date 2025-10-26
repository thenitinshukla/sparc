#include "../../include/ParticleSystem.h"
#include <numeric>
#include <cmath>
#include <vector>
#include <execution>
#include <algorithm>

void updateElectricField(ParticleSystem& ps) {
    // Compute radius squared for all particles in parallel
    std::vector<double> r2(ps.n_particles);
    std::vector<int> indices(ps.n_particles);
    std::iota(indices.begin(), indices.end(), 0);
    
    std::for_each(
        std::execution::par_unseq,
        indices.begin(), indices.end(),
        [&](int i) {
            r2[i] = ps.x[i] * ps.x[i] + ps.y[i] * ps.y[i] + ps.z[i] * ps.z[i];
        }
    );
    
    // Compute cumulative sum of charges (this part is inherently sequential)
    // But we can parallelize the division by r2
    std::vector<double> cumsum(ps.n_particles);
    cumsum[0] = ps.q[0];
    for (int i = 1; i < ps.n_particles; i++) {
        cumsum[i] = cumsum[i-1] + ps.q[i];
    }
    
    // Compute electric field in parallel
    std::for_each(
        std::execution::par_unseq,
        indices.begin(), indices.end(),
        [&](int i) {
            ps.Er[i] = cumsum[i] / r2[i];
        }
    );
}
