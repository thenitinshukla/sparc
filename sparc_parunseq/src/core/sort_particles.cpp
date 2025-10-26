#include "../../include/ParticleSystem.h"
#include <algorithm>
#include <vector>
#include <numeric>
#include <execution>

void sortParticles(ParticleSystem& ps) {
    // Compute radius squared for all particles
    std::vector<double> r2(ps.n_particles);
    std::vector<int> indices(ps.n_particles);
    std::iota(indices.begin(), indices.end(), 0);
    
    // Compute r2 in parallel
    std::for_each(
        std::execution::par_unseq,
        indices.begin(), indices.end(),
        [&](int i) {
            r2[i] = ps.x[i] * ps.x[i] + ps.y[i] * ps.y[i] + ps.z[i] * ps.z[i];
        }
    );
    
    // Create index array and sort based on r2
    // Note: parallel sort for the sorting itself
    std::sort(
        std::execution::par_unseq,
        indices.begin(), indices.end(),
        [&r2](int i, int j) {
            return r2[i] < r2[j];
        }
    );
    
    // Reorder arrays based on sorted indices
    std::vector<double> x_sorted(ps.n_particles);
    std::vector<double> y_sorted(ps.n_particles);
    std::vector<double> z_sorted(ps.n_particles);
    std::vector<double> vx_sorted(ps.n_particles);
    std::vector<double> vy_sorted(ps.n_particles);
    std::vector<double> vz_sorted(ps.n_particles);
    std::vector<double> q_sorted(ps.n_particles);
    
    // Parallel gather operation
    std::vector<int> gather_indices(ps.n_particles);
    std::iota(gather_indices.begin(), gather_indices.end(), 0);
    
    std::for_each(
        std::execution::par_unseq,
        gather_indices.begin(), gather_indices.end(),
        [&](int i) {
            int idx = indices[i];
            x_sorted[i] = ps.x[idx];
            y_sorted[i] = ps.y[idx];
            z_sorted[i] = ps.z[idx];
            vx_sorted[i] = ps.vx[idx];
            vy_sorted[i] = ps.vy[idx];
            vz_sorted[i] = ps.vz[idx];
            q_sorted[i] = ps.q[idx];
        }
    );
    
    // Copy sorted data back
    ps.x = x_sorted;
    ps.y = y_sorted;
    ps.z = z_sorted;
    ps.vx = vx_sorted;
    ps.vy = vy_sorted;
    ps.vz = vz_sorted;
    ps.q = q_sorted;
}
