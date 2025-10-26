#ifndef MEMORY_POOL_ALLOCATOR_H
#define MEMORY_POOL_ALLOCATOR_H

#include <cstddef>
#include <new>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <type_traits>

// Custom memory pool allocator for efficient memory management
template <typename T>
class MemoryPoolAllocator {
private:
    struct Block {
        Block* next;
    };

    char* memory_pool;          // The actual memory pool
    size_t pool_size;           // Total size of the pool
    size_t block_size;          // Size of each block (sizeof(T) rounded up)
    Block* free_list;           // Linked list of free blocks
    size_t allocated_blocks;    // Number of currently allocated blocks

public:
    // Type definitions for STL compatibility
    using value_type = T;
    using pointer = T*;
    using const_pointer = const T*;
    using reference = T&;
    using const_reference = const T&;
    using size_type = std::size_t;
    using difference_type = std::ptrdiff_t;

    // Rebind allocator to different type
    template <typename U>
    struct rebind {
        using other = MemoryPoolAllocator<U>;
    };

    // Default constructor
    MemoryPoolAllocator() noexcept : memory_pool(nullptr), pool_size(0), block_size(0), free_list(nullptr), allocated_blocks(0) {}

    // Constructor
    explicit MemoryPoolAllocator(size_t pool_size_bytes) 
        : pool_size(pool_size_bytes), 
          block_size((sizeof(T) + sizeof(Block*) - 1) / sizeof(Block*) * sizeof(Block*)),
          free_list(nullptr),
          allocated_blocks(0) {
        
        // Allocate the memory pool
        memory_pool = static_cast<char*>(std::malloc(pool_size));
        if (!memory_pool) {
            throw std::bad_alloc();
        }
        
        // Initialize the free list
        initialize_free_list();
    }

    // Copy constructor
    template <typename U>
    MemoryPoolAllocator(const MemoryPoolAllocator<U>& other) noexcept
        : memory_pool(other.memory_pool),
          pool_size(other.pool_size),
          block_size(sizeof(T)),
          free_list(nullptr),
          allocated_blocks(0) {
        initialize_free_list();
    }

    // Destructor
    ~MemoryPoolAllocator() {
        if (memory_pool) {
            std::free(memory_pool);
            memory_pool = nullptr;
        }
    }

    // Allocate memory
    T* allocate(std::size_t n) {
        if (n == 0) return nullptr;
        if (n > 1) {
            // For simplicity, we only handle single element allocation
            // For arrays, fall back to standard allocation
            return static_cast<T*>(std::malloc(n * sizeof(T)));
        }

        if (free_list == nullptr) {
            // Pool is exhausted, fall back to standard allocation
            return static_cast<T*>(std::malloc(sizeof(T)));
        }

        // Get a block from the free list
        Block* block = free_list;
        free_list = free_list->next;
        allocated_blocks++;

        return reinterpret_cast<T*>(block);
    }

    // Deallocate memory
    void deallocate(T* ptr, std::size_t n) {
        if (ptr == nullptr) return;
        if (n > 1) {
            // This was allocated with malloc, so deallocate with free
            std::free(ptr);
            return;
        }

        // Check if this pointer belongs to our pool
        char* char_ptr = reinterpret_cast<char*>(ptr);
        if (char_ptr >= memory_pool && char_ptr < memory_pool + pool_size) {
            // Return the block to the free list
            Block* block = reinterpret_cast<Block*>(ptr);
            block->next = free_list;
            free_list = block;
            allocated_blocks--;
        } else {
            // This was allocated with malloc, so deallocate with free
            std::free(ptr);
        }
    }

    // Construct an object
    template <typename U, typename... Args>
    void construct(U* ptr, Args&&... args) {
        new(ptr) U(std::forward<Args>(args)...);
    }

    // Destroy an object
    template <typename U>
    void destroy(U* ptr) {
        ptr->~U();
    }

    // Comparison operators
    template <typename U>
    bool operator==(const MemoryPoolAllocator<U>& other) const noexcept {
        return memory_pool == other.memory_pool;
    }

    template <typename U>
    bool operator!=(const MemoryPoolAllocator<U>& other) const noexcept {
        return !(*this == other);
    }

private:
    // Initialize the free list with all blocks in the pool
    void initialize_free_list() {
        if (block_size == 0 || pool_size < block_size) {
            free_list = nullptr;
            return;
        }

        size_t num_blocks = pool_size / block_size;
        free_list = nullptr;

        // Build the free list by linking all blocks
        for (size_t i = 0; i < num_blocks; ++i) {
            Block* block = reinterpret_cast<Block*>(memory_pool + i * block_size);
            block->next = free_list;
            free_list = block;
        }
    }
};

#endif // MEMORY_POOL_ALLOCATOR_H