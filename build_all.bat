@echo off
REM ============================================================================
REM SPARC Master Build Script for Windows
REM Builds all implementations
REM ============================================================================

setlocal enabledelayedexpansion

echo ========================================================================
echo          SPARC Master Build Script (Windows)
echo          Building All Implementations
echo ========================================================================
echo.

set SPARC_ROOT=%~dp0
set BUILD_LOG=%SPARC_ROOT%build_log.txt
set SUCCESS_COUNT=0
set FAIL_COUNT=0

REM Clear log
type nul > "%BUILD_LOG%"

REM ============================================================================
REM Build Functions
REM ============================================================================

echo ========================================================================
echo System Information
echo ========================================================================
echo Compiler:
gcc --version 2>nul || echo GCC not found
echo.
echo CMake:
cmake --version 2>nul || echo CMake not found
echo.
echo Python:
python --version 2>nul || echo Python not found
echo.

REM ============================================================================
REM Build main_sparc_serial
REM ============================================================================

echo ========================================================================
echo Building main_sparc_serial
echo ========================================================================
cd /d "%SPARC_ROOT%\main_sparc_serial"
if exist Makefile (
    mingw32-make clean >nul 2>&1
    mingw32-make -j4 >> "%BUILD_LOG%" 2>&1
    if !ERRORLEVEL! == 0 (
        echo [SUCCESS] main_sparc_serial built successfully
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAIL] main_sparc_serial build failed
        set /a FAIL_COUNT+=1
    )
) else (
    echo [SKIP] No Makefile found
)
echo.

REM ============================================================================
REM Build sparc_std
REM ============================================================================

echo ========================================================================
echo Building sparc_std
echo ========================================================================
cd /d "%SPARC_ROOT%\sparc_std"
if exist Makefile (
    mingw32-make clean >nul 2>&1
    mingw32-make -j4 >> "%BUILD_LOG%" 2>&1
    if !ERRORLEVEL! == 0 (
        echo [SUCCESS] sparc_std built successfully
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAIL] sparc_std build failed
        set /a FAIL_COUNT+=1
    )
) else (
    echo [SKIP] No Makefile found
)
echo.

REM ============================================================================
REM Build sparc_memoryPool
REM ============================================================================

echo ========================================================================
echo Building sparc_memoryPool
echo ========================================================================
cd /d "%SPARC_ROOT%\sparc_memoryPool"
if exist Makefile (
    mingw32-make clean >nul 2>&1
    mingw32-make -j4 >> "%BUILD_LOG%" 2>&1
    if !ERRORLEVEL! == 0 (
        echo [SUCCESS] sparc_memoryPool built successfully
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAIL] sparc_memoryPool build failed
        set /a FAIL_COUNT+=1
    )
) else (
    echo [SKIP] No Makefile found
)
echo.

REM ============================================================================
REM Build sparc_parallel
REM ============================================================================

echo ========================================================================
echo Building sparc_parallel
echo ========================================================================
cd /d "%SPARC_ROOT%\sparc_parallel"
if exist Makefile (
    mingw32-make clean >nul 2>&1
    mingw32-make -j4 >> "%BUILD_LOG%" 2>&1
    if !ERRORLEVEL! == 0 (
        echo [SUCCESS] sparc_parallel built successfully
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAIL] sparc_parallel build failed
        set /a FAIL_COUNT+=1
    )
) else (
    echo [SKIP] No Makefile found
)
echo.

REM ============================================================================
REM Build sparc_parunseq
REM ============================================================================

echo ========================================================================
echo Building sparc_parunseq
echo ========================================================================
cd /d "%SPARC_ROOT%\sparc_parunseq"
if exist makefile (
    mingw32-make clean >nul 2>&1
    mingw32-make -j4 >> "%BUILD_LOG%" 2>&1
    if !ERRORLEVEL! == 0 (
        echo [SUCCESS] sparc_parunseq built successfully
        set /a SUCCESS_COUNT+=1
    ) else (
        echo [FAIL] sparc_parunseq build failed
        set /a FAIL_COUNT+=1
    )
) else (
    echo [SKIP] No Makefile found
)
echo.

REM ============================================================================
REM Summary
REM ============================================================================

cd /d "%SPARC_ROOT%"

echo ========================================================================
echo Build Summary
echo ========================================================================
echo.
set /a TOTAL=%SUCCESS_COUNT% + %FAIL_COUNT%
echo Total implementations: !TOTAL!
echo Successful builds: %SUCCESS_COUNT%
echo Failed builds: %FAIL_COUNT%
echo.
echo Detailed log: %BUILD_LOG%
echo.

if %FAIL_COUNT% == 0 (
    echo [SUCCESS] All implementations built successfully!
    echo.
    echo Next steps:
    echo   1. Run benchmarks: cd benchmark ^&^& python benchmark_runner.py
    echo   2. Compare results: cd benchmark ^&^& python compare_all_results.py
    echo   3. Visualize: cd visualization ^&^& python opengl_realtime_animation.py
    echo.
) else (
    echo [WARNING] Some implementations failed to build
    echo Check %BUILD_LOG% for details
    echo.
)

pause
