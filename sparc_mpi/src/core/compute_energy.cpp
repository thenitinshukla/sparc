#include "../../include/ParticleSystem.h"
#include <cmath>
#include <cstdlib>
#include <vector>

// ============================================================================
// Compute total energy (kinetic + potential) 
// 
// This implementation uses the EXACT same O(N²) formula as the serial version
// for correctness verification. The work is distributed across MPI ranks.
// 
// For large N (10M+), set USE_FAST_ENERGY=1 to use O(N) approximation.
// ============================================================================

#ifndef USE_FAST_ENERGY
#define USE_FAST_ENERGY 0  // Set to 1 for O(N) approximation, 0 for exact O(N²)
#endif

double computeEnergyParallel(const ParticleSystem& ps, const MPIContext& mpi) {
    const int n = ps.n_particles;
    
    // ========================================================================
    // KINETIC ENERGY: 0.5 * m * v^2 (same as serial)
    // ========================================================================
    double local_kinetic = 0.0;
    for (int i = 0; i < n; i++) {
        double v2 = ps.vx[i] * ps.vx[i] + ps.vy[i] * ps.vy[i] + ps.vz[i] * ps.vz[i];
        // mass = |iqom * q| (since iqom = m/q, so m = |iqom * q|)
        local_kinetic += 0.5 * std::abs(ps.iqom * ps.q[i]) * v2;
    }
    
    double global_kinetic = 0.0;
    MPI_Allreduce(&local_kinetic, &global_kinetic, 1, MPI_DOUBLE, MPI_SUM, mpi.comm);
    
    // ========================================================================
    // POTENTIAL ENERGY
    // ========================================================================
    
#if USE_FAST_ENERGY
    // ========================================================================
    // O(N) APPROXIMATION - For large N (10M+ particles)
    // Uses Gauss's law approximation: U ≈ Σ q[i] * Q_inner[i] / r[i]
    // ========================================================================
    
    // Compute total local charge for prefix sum
    double local_charge = 0.0;
    for (int i = 0; i < n; i++) {
        local_charge += ps.q[i];
    }
    
    // Get charge sum from all previous ranks using Exscan
    double prefix_from_prev_ranks = 0.0;
    MPI_Exscan(&local_charge, &prefix_from_prev_ranks, 1, MPI_DOUBLE, MPI_SUM, mpi.comm);
    if (mpi.rank == 0) {
        prefix_from_prev_ranks = 0.0;
    }
    
    // Compute potential energy using prefix sum
    double local_potential = 0.0;
    double Q_inner = prefix_from_prev_ranks;
    
    for (int i = 0; i < n; i++) {
        double r = std::sqrt(ps.r2[i]);
        if (r > 1e-15) {
            local_potential += ps.q[i] * Q_inner / r;
        }
        Q_inner += ps.q[i];
    }
    
    double global_potential = 0.0;
    MPI_Allreduce(&local_potential, &global_potential, 1, MPI_DOUBLE, MPI_SUM, mpi.comm);
    
    return global_kinetic + global_potential;
    
#else
    // ========================================================================
    // EXACT O(N²) CALCULATION - Matches serial version exactly
    // U = 0.5 * Σ_{i≠j} q[i] * q[j] / |r[i] - r[j]|
    // ========================================================================
    
    // Gather particle counts from all ranks
    std::vector<int> recv_counts(mpi.size);
    int local_n = n;
    MPI_Allgather(&local_n, 1, MPI_INT, recv_counts.data(), 1, MPI_INT, mpi.comm);
    
    // Calculate displacements
    std::vector<int> displs(mpi.size);
    int total_particles = 0;
    for (int i = 0; i < mpi.size; i++) {
        displs[i] = total_particles;
        total_particles += recv_counts[i];
    }
    
    // Gather all positions and charges from all ranks
    std::vector<double> all_x(total_particles);
    std::vector<double> all_y(total_particles);
    std::vector<double> all_z(total_particles);
    std::vector<double> all_q(total_particles);
    
    MPI_Allgatherv(ps.x.data(), n, MPI_DOUBLE,
                   all_x.data(), recv_counts.data(), displs.data(), MPI_DOUBLE, mpi.comm);
    MPI_Allgatherv(ps.y.data(), n, MPI_DOUBLE,
                   all_y.data(), recv_counts.data(), displs.data(), MPI_DOUBLE, mpi.comm);
    MPI_Allgatherv(ps.z.data(), n, MPI_DOUBLE,
                   all_z.data(), recv_counts.data(), displs.data(), MPI_DOUBLE, mpi.comm);
    MPI_Allgatherv(ps.q.data(), n, MPI_DOUBLE,
                   all_q.data(), recv_counts.data(), displs.data(), MPI_DOUBLE, mpi.comm);
    
    // Compute potential energy: distribute O(N²) work across ranks
    // Each rank computes pairs where first index i falls in its range
    double local_potential = 0.0;
    int my_start = displs[mpi.rank];
    int my_end = my_start + recv_counts[mpi.rank];
    
    for (int i = my_start; i < my_end; i++) {
        for (int j = 0; j < total_particles; j++) {
            if (i != j) {
                double dx = all_x[i] - all_x[j];
                double dy = all_y[i] - all_y[j];
                double dz = all_z[i] - all_z[j];
                double rij = std::sqrt(dx * dx + dy * dy + dz * dz);
                if (rij > 1e-15) {
                    // Factor 0.5 because we count each pair twice (i,j) and (j,i)
                    local_potential += 0.5 * all_q[i] * all_q[j] / rij;
                }
            }
        }
    }
    
    double global_potential = 0.0;
    MPI_Allreduce(&local_potential, &global_potential, 1, MPI_DOUBLE, MPI_SUM, mpi.comm);
    
    return global_kinetic + global_potential;
    
#endif
}
