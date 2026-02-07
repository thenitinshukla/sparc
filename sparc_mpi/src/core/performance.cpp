#include "../../include/ParticleSystem.h"
#include <iostream>
#include <iomanip>

PerformanceMetricsSummary calculatePerformanceMetrics(int Nt, long long N, 
                                                       int num_species, double total_time) {
    PerformanceMetricsSummary metrics;
    metrics.total_time = total_time;

    // FLOP estimation per timestep:
    // - Sort: O(N log N) comparisons, roughly 20 FLOPs per comparison
    // - Electric field: N additions + N divisions = 2N FLOPs
    // - Position update: ~20 FLOPs per particle (sqrt, div, muls, adds)
    // Total per timestep: ~25N FLOPs (conservative estimate)
    double flops_per_step = 25.0 * N * num_species;
    double total_flops = flops_per_step * Nt;
    metrics.gflops = total_flops / (total_time * 1e9);

    // Memory bandwidth estimation:
    // Each particle has 9 doubles = 72 bytes
    // Each timestep reads and writes all particle data multiple times
    double bytes_per_step = 72.0 * N * num_species * 4;  // read/write multiple times
    double total_bytes = bytes_per_step * Nt;
    metrics.memory_bandwidth = total_bytes / (total_time * 1e9);

    return metrics;
}

void printPerformanceSummary(const PerformanceMetricsSummary& metrics, const MPIContext& mpi) {
    if (mpi.rank == 0) {
        std::cout << "\n=== Performance Summary ===" << std::endl;
        std::cout << "Total execution time: " << std::fixed << std::setprecision(3) 
                  << metrics.total_time << " seconds" << std::endl;
        std::cout << "Throughput: " << std::fixed << std::setprecision(3) 
                  << metrics.gflops << " GFLOPS" << std::endl;
        std::cout << "Memory bandwidth: " << std::fixed << std::setprecision(3) 
                  << metrics.memory_bandwidth << " GB/s" << std::endl;
        std::cout << "MPI processes: " << mpi.size << std::endl;
        std::cout << "===========================\n" << std::endl;
    }
}
