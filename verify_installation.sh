#!/bin/bash
################################################################################
# SPARC Installation Verification Script
# Checks if all components are properly installed and working
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SPARC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║         SPARC Installation Verification                                ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo

check_pass() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    ((PASS_COUNT++))
}

check_fail() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    ((FAIL_COUNT++))
}

check_warn() {
    echo -e "${YELLOW}[⚠ WARN]${NC} $1"
    ((WARN_COUNT++))
}

check_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

section() {
    echo
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

################################################################################
# Check System Requirements
################################################################################

section "System Requirements"

# Check GCC
if command -v gcc &> /dev/null; then
    version=$(gcc --version | head -1)
    check_pass "GCC found: $version"
else
    check_fail "GCC not found"
fi

# Check G++
if command -v g++ &> /dev/null; then
    version=$(g++ --version | head -1)
    check_pass "G++ found: $version"
else
    check_fail "G++ not found"
fi

# Check CMake
if command -v cmake &> /dev/null; then
    version=$(cmake --version | head -1)
    check_pass "CMake found: $version"
else
    check_warn "CMake not found (optional for some builds)"
fi

# Check Make
if command -v make &> /dev/null; then
    check_pass "Make found"
else
    check_fail "Make not found"
fi

# Check Python
if command -v python3 &> /dev/null; then
    version=$(python3 --version)
    check_pass "Python3 found: $version"
else
    check_warn "Python3 not found (required for visualization)"
fi

# Check TBB
if ldconfig -p 2>/dev/null | grep -q libtbb; then
    check_pass "Intel TBB library found"
elif [ -f "/usr/lib/libtbb.so" ] || [ -f "/usr/local/lib/libtbb.so" ]; then
    check_pass "Intel TBB library found"
else
    check_warn "Intel TBB not found (required for some implementations)"
fi

################################################################################
# Check Python Packages
################################################################################

section "Python Packages"

if command -v python3 &> /dev/null; then
    for package in numpy matplotlib pandas scipy pygame; do
        if python3 -c "import $package" 2>/dev/null; then
            check_pass "Python package '$package' installed"
        else
            check_warn "Python package '$package' not found"
        fi
    done
    
    # Check PyOpenGL separately (import name is different)
    if python3 -c "import OpenGL" 2>/dev/null; then
        check_pass "Python package 'PyOpenGL' installed"
    else
        check_warn "Python package 'PyOpenGL' not found"
    fi
fi

################################################################################
# Check Documentation Files
################################################################################

section "Documentation Files"

docs=("README.md" "ReadTheDocs.md" "QUICKSTART.md" "IMPLEMENTATION_SUMMARY.md")
for doc in "${docs[@]}"; do
    if [ -f "$SPARC_ROOT/$doc" ]; then
        check_pass "Documentation file '$doc' exists"
    else
        check_fail "Documentation file '$doc' missing"
    fi
done

################################################################################
# Check Build Files
################################################################################

section "Build Configuration Files"

# Check CMakeLists.txt files
for dir in main_sparc_serial sparc_std sparc_memoryPool sparc_parallel sparc_parunseq; do
    cmake_file="$SPARC_ROOT/$dir/CMakeLists.txt"
    if [ -f "$cmake_file" ]; then
        check_pass "CMakeLists.txt exists in $dir"
    else
        check_warn "CMakeLists.txt missing in $dir"
    fi
done

# Check Makefiles
for dir in main_sparc_serial sparc_std sparc_memoryPool sparc_parallel sparc_parunseq; do
    if [ -f "$SPARC_ROOT/$dir/Makefile" ] || [ -f "$SPARC_ROOT/$dir/makefile" ]; then
        check_pass "Makefile exists in $dir"
    else
        check_warn "Makefile missing in $dir"
    fi
done

################################################################################
# Check Executables
################################################################################

section "Compiled Executables"

executables=(
    "main_sparc_serial/sparc_cpp"
    "sparc_std/sparc_cpp"
    "sparc_memoryPool/sparc_mempool"
    "sparc_parallel/sparc_parallel"
    "sparc_parunseq/sparc_parunseq"
)

for exe in "${executables[@]}"; do
    full_path="$SPARC_ROOT/$exe"
    if [ -f "$full_path" ]; then
        if [ -x "$full_path" ]; then
            check_pass "Executable '$exe' exists and is executable"
        else
            check_warn "Executable '$exe' exists but is not executable"
        fi
    else
        check_info "Executable '$exe' not found (run build_all.sh to build)"
    fi
done

################################################################################
# Check Scripts
################################################################################

section "Utility Scripts"

scripts=(
    "build_all.sh"
    "verify_installation.sh"
    "benchmark/benchmark.sh"
    "benchmark/benchmark_cluster_all.sh"
)

for script in "${scripts[@]}"; do
    if [ -f "$SPARC_ROOT/$script" ]; then
        check_pass "Script '$script' exists"
    else
        check_fail "Script '$script' missing"
    fi
done

################################################################################
# Check Visualization Tools
################################################################################

section "Visualization Tools"

viz_scripts=(
    "visualization/opengl_realtime_animation.py"
    "visualization/visualize.py"
    "visualization/create_gif.py"
)

for script in "${viz_scripts[@]}"; do
    if [ -f "$SPARC_ROOT/$script" ]; then
        check_pass "Visualization script '$(basename $script)' exists"
    else
        check_warn "Visualization script '$(basename $script)' missing"
    fi
done

################################################################################
# Check Benchmark Tools
################################################################################

section "Benchmark Tools"

bench_scripts=(
    "benchmark/compare_all_results.py"
    "benchmark/benchmark_runner.py"
    "benchmark/visualize_benchmarks.py"
)

for script in "${bench_scripts[@]}"; do
    if [ -f "$SPARC_ROOT/$script" ]; then
        check_pass "Benchmark script '$(basename $script)' exists"
    else
        check_warn "Benchmark script '$(basename $script)' missing"
    fi
done

################################################################################
# Check Test Cases
################################################################################

section "Test Cases"

if [ -d "$SPARC_ROOT/testcase" ]; then
    check_pass "Test case directory exists"
    test_count=$(find "$SPARC_ROOT/testcase" -name "*.txt" | wc -l)
    check_info "Found $test_count test input files"
else
    check_warn "Test case directory not found"
fi

################################################################################
# Summary
################################################################################

section "Verification Summary"

echo
total=$((PASS_COUNT + FAIL_COUNT + WARN_COUNT))
echo "Total checks: $total"
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${YELLOW}Warnings: $WARN_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"
echo

if [ $FAIL_COUNT -eq 0 ]; then
    if [ $WARN_COUNT -eq 0 ]; then
        echo -e "${GREEN}✓ EXCELLENT! Everything is properly installed.${NC}"
        echo
        echo "Next steps:"
        echo "  1. Build all implementations: ./build_all.sh"
        echo "  2. Run a quick test: cd main_sparc_serial && ./sparc_cpp input_file.txt"
        echo "  3. Visualize: cd visualization && python opengl_realtime_animation.py"
        exit 0
    else
        echo -e "${GREEN}✓ GOOD! Core components are installed.${NC}"
        echo -e "${YELLOW}⚠ Some optional components have warnings.${NC}"
        echo
        echo "To install missing optional components:"
        echo "  - Intel TBB: sudo apt install libtbb-dev"
        echo "  - Python packages: pip3 install numpy matplotlib pandas scipy pygame PyOpenGL"
        echo
        echo "You can still use most features. See QUICKSTART.md for details."
        exit 0
    fi
else
    echo -e "${RED}✗ INSTALLATION INCOMPLETE${NC}"
    echo
    echo "Please address the failed checks above."
    echo "See QUICKSTART.md for installation instructions."
    exit 1
fi
