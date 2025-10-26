#include "../../include/ParticleSystem.h"
#include <numeric>
#include <cmath>

void updateElectricField(ParticleSystem& ps) {
    std::vector<double> r2 = ps.computeSquareRadius();
    double sum = 0;

    for (int i = 0; i < ps.n_particles; i++) {
        sum += ps.q[i];
        ps.Er[i] = sum / r2[i];
    }
}