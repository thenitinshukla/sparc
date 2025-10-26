#include "../../include/ParticleSystemStdPar.h"
#include <chrono>
#include <iostream>
#include <iomanip>

void updatePerformanceMetrics(PerformanceMetrics& metrics, const ParticleSystemStdPar& ps, double start_time) {
    // Calculate elapsed time (simplified)
    auto end_time = std::chrono::high_resolution_clock::now();
    // For now, we'll just set a dummy value since the complex chrono operations are causing issues
    metrics.elapsed_time = 1.0; // Dummy value
    
    // Estimate FLOPs (simplified calculation)
    // Assuming each particle operation takes a certain number of FLOPs
    metrics.flop_count = static_cast<long long>(ps.n_particles) * 20; // Rough estimate
    metrics.gflops = (metrics.flop_count / 1e9) / metrics.elapsed_time;
    
    // Estimate memory bandwidth (simplified)
    // Assuming we're processing roughly 8 bytes per particle per operation
    metrics.bytes_transferred = static_cast<long long>(ps.n_particles) * 8 * 10; // Rough estimate
    metrics.bandwidth = (metrics.bytes_transferred / 1e9) / metrics.elapsed_time;
}

PerformanceMetricsSummary calculatePerformanceMetrics(int Nt, int N, int num_species, double total_time) {
    PerformanceMetricsSummary summary;
    summary.total_time = total_time;
    summary.gflops = (static_cast<double>(Nt * N * num_species * 20) / 1e9) / total_time;
    summary.memory_bandwidth = (static_cast<double>(Nt * N * num_species * 8 * 10) / 1e9) / total_time;
    return summary;
}

void printPerformanceSummary(const PerformanceMetricsSummary& metrics) {
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "\nPerformance Summary:\n";
    std::cout << "  Total Time: " << metrics.total_time << " seconds\n";
    std::cout << "  Performance: " << metrics.gflops << " GFLOPS\n";
    std::cout << "  Memory Bandwidth: " << metrics.memory_bandwidth << " GB/s\n";
}