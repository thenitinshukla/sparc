#include "../../include/ParticleSystem.h"
#include <cmath>

// Update electric field using MPI_Scan for distributed prefix sum
// After sorting, each rank owns a contiguous shell sorted by r^2
// Er[i] = (sum of charges from r=0 to r[i]) / r^2[i]

void updateElectricFieldParallel(ParticleSystem& ps, const MPIContext& mpi) {
    const int n = ps.n_particles;

    // Step 1: Compute local prefix sum of charge
    double local_sum = 0.0;
    for (int i = 0; i < n; i++) {
        local_sum += ps.q[i];
    }

    // Step 2: Use MPI_Exscan to get the sum of charges from all previous ranks
    double prefix_sum = 0.0;
    MPI_Exscan(&local_sum, &prefix_sum, 1, MPI_DOUBLE, MPI_SUM, mpi.comm);
    // Note: On rank 0, prefix_sum is undefined after Exscan, but we initialize it to 0

    if (mpi.rank == 0) {
        prefix_sum = 0.0;
    }

    // Step 3: Local computation of Er with offset from previous ranks
    double cumulative = prefix_sum;
    for (int i = 0; i < n; i++) {
        cumulative += ps.q[i];
        // Avoid division by zero for particles at origin
        if (ps.r2[i] > 1e-30) {
            ps.Er[i] = cumulative / ps.r2[i];
        } else {
            ps.Er[i] = 0.0;
        }
    }
}
