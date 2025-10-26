#include "../../include/ParticleSystemStdPar.h"
#include "../../include/memory_pool/MemoryPoolAllocator.h"

// Static memory pool allocator for all particle data
static MemoryPoolAllocator<double> particleAllocator(1024 * 1024 * sizeof(double)); // 1MB pool

// Constructor
ParticleSystemStdPar::ParticleSystemStdPar(int max_particles, const char* species_name, double inv_qom)
    : iqom(inv_qom), n_particles(max_particles) {
    // Copy the species name (simple implementation)
    int i = 0;
    while (species_name[i] != '\0' && i < sizeof(name) - 1) {
        name[i] = species_name[i];
        i++;
    }
    name[i] = '\0'; // Ensure null termination
    
    // Allocate all arrays using our custom memory pool allocator
    x = particleAllocator.allocate(max_particles);
    y = particleAllocator.allocate(max_particles);
    z = particleAllocator.allocate(max_particles);
    vx = particleAllocator.allocate(max_particles);
    vy = particleAllocator.allocate(max_particles);
    vz = particleAllocator.allocate(max_particles);
    q = particleAllocator.allocate(max_particles);
    Er = particleAllocator.allocate(max_particles);
    
    // Initialize velocities to 0
    for (int i = 0; i < max_particles; i++) {
        vx[i] = 0.0;
        vy[i] = 0.0;
        vz[i] = 0.0;
    }
}

// Destructor
ParticleSystemStdPar::~ParticleSystemStdPar() {
    // Deallocate all arrays using our custom memory pool allocator
    particleAllocator.deallocate(x, n_particles);
    particleAllocator.deallocate(y, n_particles);
    particleAllocator.deallocate(z, n_particles);
    particleAllocator.deallocate(vx, n_particles);
    particleAllocator.deallocate(vy, n_particles);
    particleAllocator.deallocate(vz, n_particles);
    particleAllocator.deallocate(q, n_particles);
    particleAllocator.deallocate(Er, n_particles);
}

// Compute square of radius for all particles
double* ParticleSystemStdPar::computeSquareRadius() const {
    double* r2 = particleAllocator.allocate(n_particles);
    for (int i = 0; i < n_particles; i++) {
        r2[i] = x[i] * x[i] + y[i] * y[i] + z[i] * z[i];
    }
    return r2;
}

// Get maximum radius squared
double ParticleSystemStdPar::getMaxRadiusSquared() const {
    double max_r2 = 0.0;
    for (int i = 0; i < n_particles; i++) {
        double r2 = x[i] * x[i] + y[i] * y[i] + z[i] * z[i];
        if (r2 > max_r2) {
            max_r2 = r2;
        }
    }
    return max_r2;
}