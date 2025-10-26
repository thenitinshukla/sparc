#include "../../include/ParticleSystem.h"
#include <chrono>
#include <iostream>
#include <cmath>

void updatePerformanceMetrics(PerformanceMetrics& metrics, const ParticleSystem& ps, double start_time) {
    auto end_time = std::chrono::high_resolution_clock::now();
    
    // Calculate elapsed time
    double end_seconds = std::chrono::duration_cast<std::chrono::microseconds>(
        end_time.time_since_epoch()).count() / 1e6;
    metrics.elapsed_time = end_seconds - start_time;

    // Calculate FLOPS
    int particles = ps.n_particles;
    metrics.flop_count = particles * (20 + 10) +
                         particles * particles * 15;

    metrics.gflops = (metrics.flop_count * 1e-9) / metrics.elapsed_time;

    // Calculate Memory Bandwidth
    metrics.bytes_transferred = particles * 8 * 8;
    metrics.bandwidth = (metrics.bytes_transferred * 1e-9) / metrics.elapsed_time;
}

void saveData(const std::string& filename, double time, double energy, const ParticleSystem& ps, const PerformanceMetrics& metrics, double max_r2) {
    FILE* fp = fopen(filename.c_str(), "a");
    if (fp == NULL) {
        std::cout << "Error opening file " << filename << std::endl;
        return;
    }

    // Write header if file is empty (check file position)
    fseek(fp, 0, SEEK_END);
    if (ftell(fp) == 0) {
        fprintf(fp, "Time(s),Energy,MaxR2,NumParticles,TotalExecutionTime(s),Throughput(GFLOPS),MemoryBandwidth(GB/s)\n");
    }

    // Write data
    fprintf(fp, "%.6f,%.6f,%.6f,%d,%.6f,%.3f,%.3f\n",
            time,
            energy,
            max_r2,  // Save the max r2 value
            ps.n_particles,
            metrics.elapsed_time,
            metrics.gflops,
            metrics.bandwidth);

    fclose(fp);
}

PerformanceMetricsSummary calculatePerformanceMetrics(int Nt, int N, int num_species, double total_time) {
    PerformanceMetricsSummary metrics;

    // Store the total execution time
    metrics.total_time = total_time;

    // Calculate GFLOPS
    double total_operations = (double)Nt * N * num_species * 100; // Approximate operations
    metrics.gflops = total_operations / (total_time * 1e9);

    // Calculate memory bandwidth
    metrics.memory_bandwidth = (double)Nt * N * num_species * sizeof(double) * 10 /
                             (total_time * 1e9); // Approximate memory bandwidth

    return metrics;
}

void printPerformanceSummary(const PerformanceMetricsSummary& metrics) {
    std::cout << "\nPerformance Summary:\n";
    std::cout << "Total Execution Time: " << metrics.total_time << " seconds\n";
    std::cout << "Computational Throughput: " << metrics.gflops << " GFLOPS\n";
    std::cout << "Memory Bandwidth: " << metrics.memory_bandwidth << " GB/s\n";
}