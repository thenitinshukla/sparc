#include "../../include/ParticleSystem.h"
#include <algorithm>
#include <cmath>
#include <vector>
#include <numeric>
#include <queue>
#include <limits>

// ============================================================================
// Optimized Parallel Sample Sort with:
// 1. Histogram-based splitter selection (no root bottleneck)
// 2. K-way merge for post-exchange sorting (O(N log P) instead of O(N log N))
// ============================================================================

// Structure for k-way merge priority queue
struct MergeElement {
    double r2;
    int source_idx;
    int chunk_id;
    
    bool operator>(const MergeElement& other) const {
        return r2 > other.r2;  // min-heap
    }
};

void sortParticlesParallel(ParticleSystem& ps, const MPIContext& mpi) {
    const int rank = mpi.rank;
    const int size = mpi.size;
    const int n = ps.n_particles;

    // Handle edge case: no particles on this rank
    if (n == 0 && size == 1) return;

    // ========================================================================
    // Step 1: Compute r^2 for all local particles
    // ========================================================================
    ps.computeSquareRadius();

    // ========================================================================
    // Step 2: Local sort by r^2 using indirect indices
    // ========================================================================
    std::vector<int> indices(n);
    std::iota(indices.begin(), indices.end(), 0);
    std::sort(indices.begin(), indices.end(), [&ps](int a, int b) {
        return ps.r2[a] < ps.r2[b];
    });

    // Reorder all arrays according to sorted indices
    auto reorder = [&indices, n](std::vector<double>& arr) {
        if (n == 0) return;
        std::vector<double> tmp(n);
        for (int i = 0; i < n; i++) tmp[i] = arr[indices[i]];
        arr.swap(tmp);
    };

    reorder(ps.x);
    reorder(ps.y);
    reorder(ps.z);
    reorder(ps.vx);
    reorder(ps.vy);
    reorder(ps.vz);
    reorder(ps.q);
    reorder(ps.Er);
    reorder(ps.r2);

    // Single rank optimization
    if (size == 1) return;

    // ========================================================================
    // Step 3: Histogram-Based Splitter Selection (replaces sample sort)
    // ========================================================================
    const int NUM_BINS = 1024;
    
    // Find local min/max r^2
    double r2_min_local = (n > 0) ? ps.r2[0] : std::numeric_limits<double>::max();
    double r2_max_local = (n > 0) ? ps.r2[n-1] : std::numeric_limits<double>::lowest();
    
    // Global min/max using Allreduce
    double r2_min_global, r2_max_global;
    MPI_Allreduce(&r2_min_local, &r2_min_global, 1, MPI_DOUBLE, MPI_MIN, mpi.comm);
    MPI_Allreduce(&r2_max_local, &r2_max_global, 1, MPI_DOUBLE, MPI_MAX, mpi.comm);
    
    // Handle edge case: all particles at same radius
    if (r2_max_global - r2_min_global < 1e-15) {
        r2_max_global = r2_min_global + 1.0;
    }
    
    // Build local histogram
    std::vector<long long> local_hist(NUM_BINS, 0);
    double bin_width = (r2_max_global - r2_min_global) / NUM_BINS;
    
    for (int i = 0; i < n; i++) {
        int bin = (int)((ps.r2[i] - r2_min_global) / bin_width);
        bin = std::max(0, std::min(bin, NUM_BINS - 1));
        local_hist[bin]++;
    }
    
    // Global histogram using Allreduce
    std::vector<long long> global_hist(NUM_BINS);
    MPI_Allreduce(local_hist.data(), global_hist.data(), NUM_BINS, MPI_LONG_LONG, MPI_SUM, mpi.comm);
    
    // Compute splitters from global histogram
    // All ranks compute the same splitters (deterministic)
    std::vector<double> splitters(size - 1);
    long long total = std::accumulate(global_hist.begin(), global_hist.end(), 0LL);
    long long target_per_rank = (total + size - 1) / size;  // ceiling division
    
    long long cumsum = 0;
    int splitter_idx = 0;
    for (int b = 0; b < NUM_BINS && splitter_idx < size - 1; b++) {
        cumsum += global_hist[b];
        if (cumsum >= target_per_rank * (splitter_idx + 1)) {
            splitters[splitter_idx++] = r2_min_global + (b + 1) * bin_width;
        }
    }
    // Fill any remaining splitters (edge case)
    while (splitter_idx < size - 1) {
        splitters[splitter_idx++] = r2_max_global;
    }

    // ========================================================================
    // Step 4: Partition particles based on splitters
    // ========================================================================
    std::vector<int> send_counts(size, 0);
    std::vector<std::vector<int>> buckets(size);
    
    for (int i = 0; i < n; i++) {
        // Binary search for destination rank
        int dest = (int)(std::lower_bound(splitters.begin(), splitters.end(), ps.r2[i]) 
                        - splitters.begin());
        buckets[dest].push_back(i);
        send_counts[dest]++;
    }

    // ========================================================================
    // Step 5: All-to-all exchange of counts
    // ========================================================================
    std::vector<int> recv_counts(size);
    MPI_Alltoall(send_counts.data(), 1, MPI_INT, recv_counts.data(), 1, MPI_INT, mpi.comm);

    // Calculate displacements
    std::vector<int> send_displs(size, 0);
    std::vector<int> recv_displs(size, 0);
    for (int i = 1; i < size; i++) {
        send_displs[i] = send_displs[i - 1] + send_counts[i - 1];
        recv_displs[i] = recv_displs[i - 1] + recv_counts[i - 1];
    }

    int total_send = (size > 0) ? send_displs[size - 1] + send_counts[size - 1] : 0;
    int total_recv = (size > 0) ? recv_displs[size - 1] + recv_counts[size - 1] : 0;

    // ========================================================================
    // Step 6: Pack send buffers (interleaved format for cache efficiency)
    // ========================================================================
    const int num_fields = 9;  // x, y, z, vx, vy, vz, q, Er, r2
    std::vector<double> send_buf(total_send * num_fields);
    
    int pos = 0;
    for (int dest = 0; dest < size; dest++) {
        for (int idx : buckets[dest]) {
            send_buf[pos++] = ps.x[idx];
            send_buf[pos++] = ps.y[idx];
            send_buf[pos++] = ps.z[idx];
            send_buf[pos++] = ps.vx[idx];
            send_buf[pos++] = ps.vy[idx];
            send_buf[pos++] = ps.vz[idx];
            send_buf[pos++] = ps.q[idx];
            send_buf[pos++] = ps.Er[idx];
            send_buf[pos++] = ps.r2[idx];
        }
    }

    // Scale counts and displacements for packed data
    std::vector<int> send_counts_packed(size), send_displs_packed(size);
    std::vector<int> recv_counts_packed(size), recv_displs_packed(size);
    for (int i = 0; i < size; i++) {
        send_counts_packed[i] = send_counts[i] * num_fields;
        send_displs_packed[i] = send_displs[i] * num_fields;
        recv_counts_packed[i] = recv_counts[i] * num_fields;
        recv_displs_packed[i] = recv_displs[i] * num_fields;
    }

    // ========================================================================
    // Step 7: Alltoallv exchange
    // ========================================================================
    std::vector<double> recv_buf(total_recv * num_fields);
    MPI_Alltoallv(send_buf.data(), send_counts_packed.data(), send_displs_packed.data(), MPI_DOUBLE,
                  recv_buf.data(), recv_counts_packed.data(), recv_displs_packed.data(), MPI_DOUBLE,
                  mpi.comm);

    // Free send buffer early
    send_buf.clear();
    send_buf.shrink_to_fit();

    // ========================================================================
    // Step 8: Unpack into temporary arrays for k-way merge
    // ========================================================================
    std::vector<double> recv_x(total_recv), recv_y(total_recv), recv_z(total_recv);
    std::vector<double> recv_vx(total_recv), recv_vy(total_recv), recv_vz(total_recv);
    std::vector<double> recv_q(total_recv), recv_Er(total_recv), recv_r2(total_recv);
    
    for (int i = 0; i < total_recv; i++) {
        int base = i * num_fields;
        recv_x[i] = recv_buf[base + 0];
        recv_y[i] = recv_buf[base + 1];
        recv_z[i] = recv_buf[base + 2];
        recv_vx[i] = recv_buf[base + 3];
        recv_vy[i] = recv_buf[base + 4];
        recv_vz[i] = recv_buf[base + 5];
        recv_q[i] = recv_buf[base + 6];
        recv_Er[i] = recv_buf[base + 7];
        recv_r2[i] = recv_buf[base + 8];
    }
    
    // Free recv buffer
    recv_buf.clear();
    recv_buf.shrink_to_fit();

    // ========================================================================
    // Step 9: K-Way Merge (O(N log P) instead of O(N log N))
    // ========================================================================
    // Each chunk from a source rank is already sorted
    // Use priority queue to merge them efficiently
    
    std::vector<int> merge_order(total_recv);
    
    if (total_recv > 0) {
        // Priority queue for k-way merge
        std::priority_queue<MergeElement, std::vector<MergeElement>, std::greater<MergeElement>> pq;
        
        // Track current position in each chunk
        std::vector<int> chunk_pos(size);
        for (int c = 0; c < size; c++) {
            chunk_pos[c] = recv_displs[c];
        }
        
        // Initialize priority queue with first element from each non-empty chunk
        for (int c = 0; c < size; c++) {
            if (recv_counts[c] > 0) {
                MergeElement elem;
                elem.r2 = recv_r2[recv_displs[c]];
                elem.source_idx = recv_displs[c];
                elem.chunk_id = c;
                pq.push(elem);
                chunk_pos[c]++;
            }
        }
        
        // Merge using priority queue
        int out_idx = 0;
        while (!pq.empty()) {
            MergeElement top = pq.top();
            pq.pop();
            
            merge_order[out_idx++] = top.source_idx;
            
            // If more elements in this chunk, add next one to queue
            int c = top.chunk_id;
            if (chunk_pos[c] < recv_displs[c] + recv_counts[c]) {
                MergeElement next_elem;
                next_elem.r2 = recv_r2[chunk_pos[c]];
                next_elem.source_idx = chunk_pos[c];
                next_elem.chunk_id = c;
                pq.push(next_elem);
                chunk_pos[c]++;
            }
        }
    }

    // ========================================================================
    // Step 10: Resize ParticleSystem and apply merge order
    // ========================================================================
    ps.resize(total_recv);
    
    for (int i = 0; i < total_recv; i++) {
        int src = merge_order[i];
        ps.x[i] = recv_x[src];
        ps.y[i] = recv_y[src];
        ps.z[i] = recv_z[src];
        ps.vx[i] = recv_vx[src];
        ps.vy[i] = recv_vy[src];
        ps.vz[i] = recv_vz[src];
        ps.q[i] = recv_q[src];
        ps.Er[i] = recv_Er[src];
        ps.r2[i] = recv_r2[src];
    }
}
