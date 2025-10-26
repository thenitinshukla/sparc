#ifndef PARTICLE_SYSTEM_H
#define PARTICLE_SYSTEM_H

#include <string>
#include <vector>
#include <memory>

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
    
    double iqom;                // inverse of charge over mass
    int n_particles;            // number of particles

    // Constructor
    ParticleSystem(int max_particles, const std::string& species_name, double inv_qom);
    
    // Compute square of radius for all particles
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
void sortParticles(ParticleSystem& ps);
void updateElectricField(ParticleSystem& ps);
void updatePositions(ParticleSystem& ps, double dt);
double computeEnergy(const ParticleSystem& ps);
void updatePerformanceMetrics(PerformanceMetrics& metrics, const ParticleSystem& ps, double start_time);
void saveData(const std::string& filename, double time, double energy, const ParticleSystem& ps, const PerformanceMetrics& metrics, double max_r2);
void saveParticlePositions(const std::string& filename, const ParticleSystem& ps, int step);
PerformanceMetricsSummary calculatePerformanceMetrics(int Nt, int N, int num_species, double total_time);
void printPerformanceSummary(const PerformanceMetricsSummary& metrics);

#endif // PARTICLE_SYSTEM_H