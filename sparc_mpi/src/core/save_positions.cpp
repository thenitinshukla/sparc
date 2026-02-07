#include "../../include/ParticleSystem.h"
#include <fstream>
#include <sstream>
#include <iomanip>

// Save particle positions - only rank 0 writes, gathers data from all ranks
void saveParticlePositions(const std::string& filename, const ParticleSystem& ps, 
                           int step, const MPIContext& mpi) {
    // Gather all particle counts
    int local_n = ps.n_particles;
    std::vector<int> all_counts(mpi.size);
    MPI_Gather(&local_n, 1, MPI_INT, all_counts.data(), 1, MPI_INT, 0, mpi.comm);

    // Calculate displacements
    std::vector<int> displs(mpi.size, 0);
    int total_n = 0;
    if (mpi.rank == 0) {
        for (int i = 0; i < mpi.size; i++) {
            displs[i] = total_n;
            total_n += all_counts[i];
        }
    }

    // Gather x, y, z positions
    std::vector<double> all_x, all_y, all_z;
    if (mpi.rank == 0) {
        all_x.resize(total_n);
        all_y.resize(total_n);
        all_z.resize(total_n);
    }

    MPI_Gatherv(ps.x.data(), local_n, MPI_DOUBLE, 
                all_x.data(), all_counts.data(), displs.data(), MPI_DOUBLE, 0, mpi.comm);
    MPI_Gatherv(ps.y.data(), local_n, MPI_DOUBLE, 
                all_y.data(), all_counts.data(), displs.data(), MPI_DOUBLE, 0, mpi.comm);
    MPI_Gatherv(ps.z.data(), local_n, MPI_DOUBLE, 
                all_z.data(), all_counts.data(), displs.data(), MPI_DOUBLE, 0, mpi.comm);

    // Write to file (binary format)
    if (mpi.rank == 0) {
        std::ofstream file(filename, std::ios::binary);
        if (file.is_open()) {
            file.write(reinterpret_cast<char*>(&step), sizeof(int));
            file.write(reinterpret_cast<char*>(&total_n), sizeof(int));
            file.write(reinterpret_cast<char*>(all_x.data()), total_n * sizeof(double));
            file.write(reinterpret_cast<char*>(all_y.data()), total_n * sizeof(double));
            file.write(reinterpret_cast<char*>(all_z.data()), total_n * sizeof(double));
            file.close();
        }
    }
}
