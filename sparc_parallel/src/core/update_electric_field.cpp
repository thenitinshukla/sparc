#include "../../include/ParticleSystemParallel.h"
#include <algorithm>
#include <execution>
#include <cmath>
#include <vector>
#include <numeric>

void updateElectricField(ParticleSystemParallel& ps) {
    // Compute radius squared for all particles
    std::vector<double> r2 = ps.computeSquareRadius();
    
    // Create a temporary vector to store cumulative charges
    std::vector<double> cumulative_charge(ps.n_particles);
    
    // Compute cumulative charge sum sequentially (this needs to be sequential)
    double sum = 0.0;
    for (int i = 0; i < ps.n_particles; i++) {
        sum += ps.q[i];
        cumulative_charge[i] = sum;
    }
    
    // Update electric field in parallel for all particles
    std::for_each(std::execution::par, ps.Er.begin(), ps.Er.end(),
                  [&](double& Eri) {
                      size_t i = static_cast<size_t>(&Eri - ps.Er.data());
                      if (i < static_cast<size_t>(ps.n_particles)) {
                          // Electric field: E_r = Q_enc(r) / r^2
                          Eri = cumulative_charge[i] / r2[i];
                      }
                  });
}