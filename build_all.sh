#!/bin/bash
################################################################################
# SPARC Master Build Script
# Builds all implementations and verifies correctness
################################################################################

# Do NOT exit on first error — we handle errors manually
#set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║         SPARC Master Build Script                                      ║"
echo "║         Building All Implementations                                   ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo

SPARC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_LOG="${SPARC_ROOT}/build_log.txt"
SUCCESS_COUNT=0
FAIL_COUNT=0

# Clear log file
> "$BUILD_LOG"

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

log_section() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# -----------------------------------------------------------------------------
# Build Function
# -----------------------------------------------------------------------------

build_implementation() {
    local name=$1
    local dir=$2
    local build_cmd=$3

    log_section "Building $name"

    if [ ! -d "$dir" ]; then
        log_error "Directory not found: $dir"
        echo "FAIL: $name - Directory not found" >> "$BUILD_LOG"
        ((FAIL_COUNT++))
        return
    fi

    cd "$dir" || {
        log_error "Failed to enter directory: $dir"
        echo "FAIL: $name - cd failed" >> "$BUILD_LOG"
        ((FAIL_COUNT++))
        return
    }

    log_info "Directory: $dir"
    log_info "Command: $build_cmd"

    # Clean previous build
    if [ -f "Makefile" ] || [ -f "makefile" ]; then
        make clean > /dev/null 2>&1 || true
    fi

    # Run the build command and capture result
    if eval "$build_cmd" >> "$BUILD_LOG" 2>&1; then
        log_success "$name built successfully"
        echo "SUCCESS: $name" >> "$BUILD_LOG"
        ((SUCCESS_COUNT++))
    else
        log_error "$name build failed (see $BUILD_LOG for details)"
        echo "FAIL: $name - Build error" >> "$BUILD_LOG"
        ((FAIL_COUNT++))
    fi

    # Always return to root
    cd "$SPARC_ROOT" || exit 1
}

# -----------------------------------------------------------------------------
# Verify Function
# -----------------------------------------------------------------------------

verify_executable() {
    local name=$1
    local executable=$2

    if [ -f "$executable" ]; then
        log_success "$name executable found: $executable"
    else
        log_error "$name executable not found: $executable"
    fi
}

# -----------------------------------------------------------------------------
# Quick Test Function
# -----------------------------------------------------------------------------

run_quick_test() {
    local name=$1
    local executable=$2
    local input=$3

    log_info "Running quick test for $name..."

    if [ ! -f "$executable" ]; then
        log_error "Executable not found: $executable"
        return
    fi

    if [ ! -f "$input" ]; then
        log_error "Input file not found: $input"
        return
    fi

    if timeout 30 "$executable" "$input" -n > "/tmp/test_${name}.txt" 2>&1; then
        if grep -q "Energy conservation error" "/tmp/test_${name}.txt"; then
            local error
            error=$(grep "Energy conservation error" "/tmp/test_${name}.txt" | tail -1 | awk '{print $(NF-1)}' | tr -d '%')
            log_success "$name test passed (Energy error: ${error}%)"
        else
            log_success "$name test completed successfully"
        fi
    else
        log_error "$name test failed or timed out"
    fi
}

# -----------------------------------------------------------------------------
# Main Build Process
# -----------------------------------------------------------------------------

log_section "System Information"
echo "OS: $(uname -s)"
echo "Compiler: $(gcc --version | head -1)"
echo "CMake: $(cmake --version | head -1 2>/dev/null || echo 'Not found')"
echo "Python: $(python3 --version 2>/dev/null || echo 'Not found')"
echo

# Build all implementations (each independent)
build_implementation "main_sparc_serial" \
    "${SPARC_ROOT}/main_sparc_serial" \
    "make -j\$(nproc)"

build_implementation "sparc_std" \
    "${SPARC_ROOT}/sparc_std" \
    "make -j\$(nproc)"

build_implementation "sparc_memoryPool" \
    "${SPARC_ROOT}/sparc_memoryPool" \
    "make -j\$(nproc)"

build_implementation "sparc_parallel" \
    "${SPARC_ROOT}/sparc_parallel" \
    "make -j\$(nproc)"

build_implementation "sparc_parunseq" \
    "${SPARC_ROOT}/sparc_parunseq" \
    "make -j\$(nproc)"

# -----------------------------------------------------------------------------
# Verify Executables
# -----------------------------------------------------------------------------

log_section "Verifying Executables"

verify_executable "main_sparc_serial" "${SPARC_ROOT}/main_sparc_serial/sparc_cpp"
verify_executable "sparc_std" "${SPARC_ROOT}/sparc_std/sparc_std"
verify_executable "sparc_memoryPool" "${SPARC_ROOT}/sparc_memoryPool/sparc_mempool"
verify_executable "sparc_parallel" "${SPARC_ROOT}/sparc_parallel/sparc_parallel"
verify_executable "sparc_parunseq" "${SPARC_ROOT}/sparc_parunseq/sparc_parunseq"

# -----------------------------------------------------------------------------
# Quick Tests
# -----------------------------------------------------------------------------

log_section "Running Quick Tests"

TEST_INPUT="${SPARC_ROOT}/test_quick.txt"
cat > "$TEST_INPUT" <<EOF
N = 1000
R = 1.0
dt = 0.001
tend = 0.05
SAVE_INTERVAL = 100
species electron 1.0
EOF

log_info "Created test input: $TEST_INPUT"

run_quick_test "serial" "${SPARC_ROOT}/main_sparc_serial/sparc_cpp" "$TEST_INPUT"
run_quick_test "parallel" "${SPARC_ROOT}/sparc_parallel/sparc_parallel" "$TEST_INPUT"
run_quick_test "parunseq" "${SPARC_ROOT}/sparc_parunseq/sparc_parunseq" "$TEST_INPUT"

# Cleanup
rm -f "$TEST_INPUT" /tmp/test_*.txt

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------

log_section "Build Summary"

echo
echo "Total implementations: $((SUCCESS_COUNT + FAIL_COUNT))"
echo -e "${GREEN}Successful builds: $SUCCESS_COUNT${NC}"
echo -e "${RED}Failed builds: $FAIL_COUNT${NC}"
echo
echo "Detailed log: $BUILD_LOG"
echo

if [ $FAIL_COUNT -eq 0 ]; then
    log_success "All implementations built successfully!"
    echo
    echo "Next steps:"
    echo "  1. Run benchmarks: cd benchmark && ./benchmark.sh"
    echo "  2. Compare results: cd benchmark && python compare_all_results.py"
    echo "  3. Visualize: cd visualization && python opengl_realtime_animation.py ../sparc_parallel/output/"
    echo
    exit 0
else
    log_error "Some implementations failed to build"
    echo "Check $BUILD_LOG for details"
    echo
    exit 1
fi

