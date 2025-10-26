#include "../../include/ParticleSystemParallel.h"
#include <algorithm>
#include <execution>
#include <cmath>

void updateVelocities(ParticleSystemParallel& ps, double dt) {
    // Precompute radius for all particles
    std::vector<double> r(ps.n_particles);
    
    // Compute radius in parallel
    std::for_each(std::execution::par, r.begin(), r.end(),
                  [&](double& ri) {
                      size_t i = static_cast<size_t>(&ri - r.data());
                      if (i < static_cast<size_t>(ps.n_particles)) {
                          ri = std::sqrt(ps.x[i] * ps.x[i] + ps.y[i] * ps.y[i] + ps.z[i] * ps.z[i]);
                      }
                  });
    
    // Update velocities in parallel
    std::for_each(std::execution::par, ps.vx.begin(), ps.vx.end(),
                  [&](double& vxi) {
                      size_t i = static_cast<size_t>(&vxi - ps.vx.data());
                      if (i < static_cast<size_t>(ps.n_particles)) {
                          // Avoid division by zero
                          if (r[i] < 1e-10) return;
                          double qom = 1.0 / ps.iqom;
                          vxi += dt * qom * ps.Er[i] * ps.x[i] / r[i];
                      }
                  });
    
    std::for_each(std::execution::par, ps.vy.begin(), ps.vy.end(),
                  [&](double& vyi) {
                      size_t i = static_cast<size_t>(&vyi - ps.vy.data());
                      if (i < static_cast<size_t>(ps.n_particles)) {
                          // Avoid division by zero
                          if (r[i] < 1e-10) return;
                          double qom = 1.0 / ps.iqom;
                          vyi += dt * qom * ps.Er[i] * ps.y[i] / r[i];
                      }
                  });
    
    std::for_each(std::execution::par, ps.vz.begin(), ps.vz.end(),
                  [&](double& vzi) {
                      size_t i = static_cast<size_t>(&vzi - ps.vz.data());
                      if (i < static_cast<size_t>(ps.n_particles)) {
                          // Avoid division by zero
                          if (r[i] < 1e-10) return;
                          double qom = 1.0 / ps.iqom;
                          vzi += dt * qom * ps.Er[i] * ps.z[i] / r[i];
                      }
                  });
}