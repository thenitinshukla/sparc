#include "../../include/ParticleSystemStdPar.h"

void updateElectricFieldStdPar(ParticleSystemStdPar& ps) {
    // Compute square of radius for all particles
    double* r2 = new double[ps.n_particles];
    for (int i = 0; i < ps.n_particles; i++) {
        r2[i] = ps.x[i] * ps.x[i] + ps.y[i] * ps.y[i] + ps.z[i] * ps.z[i];
    }
    
    double sum = 0;
    for (int i = 0; i < ps.n_particles; i++) {
        sum += ps.q[i];
        ps.Er[i] = sum / r2[i];
    }
    
    delete[] r2;
}