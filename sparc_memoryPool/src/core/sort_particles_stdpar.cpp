#include "../../include/ParticleSystemStdPar.h"

void sortParticlesStdPar(ParticleSystemStdPar& ps) {
    // Compute square of radius for all particles
    double* r2 = new double[ps.n_particles];
    for (int i = 0; i < ps.n_particles; i++) {
        r2[i] = ps.x[i] * ps.x[i] + ps.y[i] * ps.y[i] + ps.z[i] * ps.z[i];
    }

    // Simple bubble sort (can be optimized with better sorting algorithm)
    for (int i = 0; i < ps.n_particles - 1; i++) {
        for (int j = 0; j < ps.n_particles - i - 1; j++) {
            if (r2[j] > r2[j + 1]) {
                // Swap all particle properties
                double temp = r2[j];
                r2[j] = r2[j + 1];
                r2[j + 1] = temp;
                
                temp = ps.x[j];
                ps.x[j] = ps.x[j + 1];
                ps.x[j + 1] = temp;
                
                temp = ps.y[j];
                ps.y[j] = ps.y[j + 1];
                ps.y[j + 1] = temp;
                
                temp = ps.z[j];
                ps.z[j] = ps.z[j + 1];
                ps.z[j + 1] = temp;
                
                temp = ps.vx[j];
                ps.vx[j] = ps.vx[j + 1];
                ps.vx[j + 1] = temp;
                
                temp = ps.vy[j];
                ps.vy[j] = ps.vy[j + 1];
                ps.vy[j + 1] = temp;
                
                temp = ps.vz[j];
                ps.vz[j] = ps.vz[j + 1];
                ps.vz[j + 1] = temp;
                
                temp = ps.q[j];
                ps.q[j] = ps.q[j + 1];
                ps.q[j + 1] = temp;
                
                temp = ps.Er[j];
                ps.Er[j] = ps.Er[j + 1];
                ps.Er[j + 1] = temp;
            }
        }
    }
    
    delete[] r2;
}