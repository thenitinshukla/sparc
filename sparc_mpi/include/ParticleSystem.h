#ifndef PARTICLE_SYSTEM_H
#define PARTICLE_SYSTEM_H

#include <string>
#include <vector>
#include <memory>
#include <mpi.h>

// Forward declarations
struct PerformanceMetrics;

// Structure for particle system using Structure of Arrays (SoA)
class ParticleSystem {
public:
    std::string name;
    
    // Arrays for particle properties (Structure of Arrays)
    std::vector<double> x;      // x positions
    std::vector<double> y;      // y positions
    std::vector<double> z;      // z positions
    std::vector<double> vx;     // x velocities
    std::vector<double> vy;     // y velocities
    std::vector<double> vz;     // z velocities
    std::vector<double> q;      // charges
    std::vector<double> Er;     // radial electric field
    std::vector<double> r2;     // cached r^2 values for sorting
    
    double iqom;                // inverse of charge over mass
    int n_particles;            // LOCAL number of particles on this rank
    long long n_total;          // GLOBAL total number of particles

    // Constructor
    ParticleSystem(int local_particles, long long total_particles, 
                   const std::string& species_name, double inv_qom);
    
    // Resize arrays for dynamic particle count after redistribution
    void resize(int new_size);
    
    // Compute square of radius for all particles
    void computeSquareRadius();
    
    // Get maximum radius squared (local)
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

// MPI context
struct MPIContext {
    int rank;
    int size;
    MPI_Comm comm;
};

// Function declarations
void sortParticlesParallel(ParticleSystem& ps, const MPIContext& mpi);
void updateElectricFieldParallel(ParticleSystem& ps, const MPIContext& mpi);
void updatePositions(ParticleSystem& ps, double dt);
double computeEnergyParallel(const ParticleSystem& ps, const MPIContext& mpi);
void saveParticlePositions(const std::string& filename, const ParticleSystem& ps, 
                           int step, const MPIContext& mpi);
PerformanceMetricsSummary calculatePerformanceMetrics(int Nt, long long N, 
                                                       int num_species, double total_time);
void printPerformanceSummary(const PerformanceMetricsSummary& metrics, const MPIContext& mpi);

#endif // PARTICLE_SYSTEM_H
