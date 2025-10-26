#ifndef PARTICLE_SYSTEM_STDPAR_H
#define PARTICLE_SYSTEM_STDPAR_H

#include <vector>
#include <string>
#include <execution>
#include <memory>
#include <algorithm>  // Added for std::transform
#include "memory_pool/MemoryPoolAllocator.h"

// Forward declarations
struct PerformanceMetrics;

// Structure for particle system using Structure of Arrays (SoA) with custom allocator
class ParticleSystemStdPar {
public:
    // Using C-style strings to avoid std::string dependency
    char name[256];
    
    // Arrays for particle properties (Structure of Arrays) using custom allocator
    std::vector<double, MemoryPoolAllocator<double>> x;      // x positions
    std::vector<double, MemoryPoolAllocator<double>> y;      // y positions
    std::vector<double, MemoryPoolAllocator<double>> z;      // z positions
    std::vector<double, MemoryPoolAllocator<double>> vx;     // x velocities
    std::vector<double, MemoryPoolAllocator<double>> vy;     // y velocities
    std::vector<double, MemoryPoolAllocator<double>> vz;     // z velocities
    std::vector<double, MemoryPoolAllocator<double>> q;      // charges
    std::vector<double, MemoryPoolAllocator<double>> Er;     // radial electric field
    
    double iqom;                // inverse of charge over mass
    int n_particles;            // number of particles

    // Constructor
    ParticleSystemStdPar(int max_particles, const char* species_name, double inv_qom);
    
    // Destructor
    ~ParticleSystemStdPar();
    
    // Compute square of radius for all particles (returning std::vector<double> instead of custom allocator version)
    std::vector<double> computeSquareRadius() const;
    
    // Get maximum radius squared
    double getMaxRadiusSquared() const;
};

// Performance metrics structure
struct PerformanceMetrics {
    double elapsed_time;        // Total execution time in seconds
    double gflops;              // Computational throughput in GFLOPS
    double bandwidth;           // Memory bandwidth in GB/s
    long long flop_count;       // Total floating point operations
    long long bytes_transferred; // Total bytes transferred
};

// Performance metrics summary
struct PerformanceMetricsSummary {
    double total_time;
    double gflops;
    double memory_bandwidth;
};

// Function declarations
void sortParticles(ParticleSystemStdPar& ps);
void updateElectricField(ParticleSystemStdPar& ps);
void updatePositions(ParticleSystemStdPar& ps, double dt);
void updateVelocities(ParticleSystemStdPar& ps, double dt);
double computeEnergy(const ParticleSystemStdPar& ps);
void updatePerformanceMetrics(PerformanceMetrics& metrics, const ParticleSystemStdPar& ps, double start_time);
void saveData(const std::string& filename, double time, double energy, const ParticleSystemStdPar& ps, const PerformanceMetrics& metrics, double max_r2);
void saveParticlePositions(const std::string& filename, const ParticleSystemStdPar& ps, int step);
PerformanceMetricsSummary calculatePerformanceMetrics(int Nt, int N, int num_species, double total_time);
void printPerformanceSummary(const PerformanceMetricsSummary& metrics);

#endif // PARTICLE_SYSTEM_STDPAR_H