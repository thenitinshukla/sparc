#ifndef MEMORY_POOL_ALLOCATOR_H
#define MEMORY_POOL_ALLOCATOR_H

template<typename T>
class MemoryPoolAllocator {
private:
    struct Block {
        Block* next;
    };

    // Pool management
    char* pool_;
    Block* free_list_;
    unsigned int pool_size_;
    unsigned int next_free_;

public:
    // Type definitions
    typedef T value_type;
    typedef T* pointer;
    typedef const T* const_pointer;
    typedef T& reference;
    typedef const T& const_reference;
    typedef unsigned int size_type;
    typedef int difference_type;

    // Rebind allocator to different type
    template<typename U>
    struct rebind {
        typedef MemoryPoolAllocator<U> other;
    };

    // Constructors
    explicit MemoryPoolAllocator(unsigned int pool_size = 1024 * sizeof(T))
        : free_list_(0), pool_size_(pool_size), next_free_(0) {
        pool_ = static_cast<char*>(operator new(pool_size));
    }

    template<typename U>
    MemoryPoolAllocator(const MemoryPoolAllocator<U>& other)
        : free_list_(0), pool_size_(other.pool_size_), next_free_(0) {
        pool_ = static_cast<char*>(operator new(pool_size_));
    }

    // Destructor
    ~MemoryPoolAllocator() {
        operator delete(pool_);
    }

    // Allocate memory
    T* allocate(unsigned int n) {
        if (n == 1) {
            if (free_list_) {
                Block* block = free_list_;
                free_list_ = free_list_->next;
                return reinterpret_cast<T*>(block);
            } else if ((next_free_ + sizeof(T)) <= pool_size_) {
                T* result = reinterpret_cast<T*>(pool_ + next_free_);
                next_free_ += sizeof(T);
                return result;
            }
        }
        
        // For larger allocations or when pool is full, use standard allocation
        return static_cast<T*>(operator new(n * sizeof(T)));
    }

    // Deallocate memory
    void deallocate(T* ptr, unsigned int n) {
        if (n == 1 && 
            reinterpret_cast<char*>(ptr) >= pool_ && 
            reinterpret_cast<char*>(ptr) < (pool_ + pool_size_)) {
            Block* block = reinterpret_cast<Block*>(ptr);
            block->next = free_list_;
            free_list_ = block;
        } else {
            // For larger deallocations or pointers outside our pool, use standard deallocation
            operator delete(ptr);
        }
    }

    // Construct object
    template<typename U, typename V>
    void construct(U* ptr, const V& value) {
        new(ptr) U(value);
    }

    // Destroy object
    template<typename U>
    void destroy(U* ptr) {
        ptr->~U();
    }

    // Comparison operators
    template<typename U>
    bool operator==(const MemoryPoolAllocator<U>&) const {
        return true; // All instances are equivalent
    }

    template<typename U>
    bool operator!=(const MemoryPoolAllocator<U>& other) const {
        return !(*this == other);
    }
};

#endif // MEMORY_POOL_ALLOCATOR_H