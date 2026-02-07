#include "../../include/ParticleSystem.h"
#include <cmath>

void updatePositions(ParticleSystem& ps, double dt) {
    const int n = ps.n_particles;
    const double qom = 1.0 / ps.iqom;

    for (int i = 0; i < n; i++) {
        double r = std::sqrt(ps.r2[i]);
        if (r > 1e-15) {
            double inv_r = 1.0 / r;
            // Update velocities
            ps.vx[i] += dt * qom * ps.Er[i] * ps.x[i] * inv_r;
            ps.vy[i] += dt * qom * ps.Er[i] * ps.y[i] * inv_r;
            ps.vz[i] += dt * qom * ps.Er[i] * ps.z[i] * inv_r;
        }
        // Update positions
        ps.x[i] += dt * ps.vx[i];
        ps.y[i] += dt * ps.vy[i];
        ps.z[i] += dt * ps.vz[i];
    }
}
