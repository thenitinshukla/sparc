#include "../../include/ParticleSystemParallel.h"
#include <vector>
#include <execution>
#include <algorithm>
#include <cmath>
#include "../../include/memory_pool/MemoryPoolAllocator.h"

// Updates particle positions in parallel using multi-threaded execution
void updatePositions(ParticleSystemParallel& ps, double dt) {
    // Get the number of particles
    int n_particles = ps.n_particles;
    
    // Update positions in parallel using current velocities
    std::for_each(std::execution::par, ps.x.begin(), ps.x.end(),
                  [&](double& xi) {
                      size_t i = static_cast<size_t>(&xi - ps.x.data());
                      if (i < static_cast<size_t>(n_particles)) {
                          xi += dt * ps.vx[i];
                      }
                  });
    
    std::for_each(std::execution::par, ps.y.begin(), ps.y.end(),
                  [&](double& yi) {
                      size_t i = static_cast<size_t>(&yi - ps.y.data());
                      if (i < static_cast<size_t>(n_particles)) {
                          yi += dt * ps.vy[i];
                      }
                  });
    
    std::for_each(std::execution::par, ps.z.begin(), ps.z.end(),
                  [&](double& zi) {
                      size_t i = static_cast<size_t>(&zi - ps.z.data());
                      if (i < static_cast<size_t>(n_particles)) {
                          zi += dt * ps.vz[i];
                      }
                  });
}