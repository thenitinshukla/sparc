#include "../../include/ParticleSystemParallel.h"
#include <algorithm>
#include <execution>
#include <vector>

void sortParticles(ParticleSystemParallel& ps) {
    // Compute radius squared for all particles
    std::vector<double> r2 = ps.computeSquareRadius();
    
    // Create index vector
    std::vector<int> indices(ps.n_particles);
    for (int i = 0; i < ps.n_particles; i++) {
        indices[i] = i;
    }
    
    // Sort indices based on radius squared using parallel execution
    std::sort(std::execution::par, indices.begin(), indices.end(),
              [&](int i, int j) { return r2[i] < r2[j]; });
    
    // Create temporary copies of all particle data
    std::vector<double, MemoryPoolAllocator<double>> x_temp = ps.x;
    std::vector<double, MemoryPoolAllocator<double>> y_temp = ps.y;
    std::vector<double, MemoryPoolAllocator<double>> z_temp = ps.z;
    std::vector<double, MemoryPoolAllocator<double>> vx_temp = ps.vx;
    std::vector<double, MemoryPoolAllocator<double>> vy_temp = ps.vy;
    std::vector<double, MemoryPoolAllocator<double>> vz_temp = ps.vz;
    std::vector<double, MemoryPoolAllocator<double>> q_temp = ps.q;
    std::vector<double, MemoryPoolAllocator<double>> Er_temp = ps.Er;
    
    // Rearrange particle data according to sorted indices
    for (int i = 0; i < ps.n_particles; i++) {
        int idx = indices[i];
        ps.x[i] = x_temp[idx];
        ps.y[i] = y_temp[idx];
        ps.z[i] = z_temp[idx];
        ps.vx[i] = vx_temp[idx];
        ps.vy[i] = vy_temp[idx];
        ps.vz[i] = vz_temp[idx];
        ps.q[i] = q_temp[idx];
        ps.Er[i] = Er_temp[idx];
    }
}