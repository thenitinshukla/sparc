# SPARC Python Implementation Results

## Simulation Overview

The Python implementation of the SPARC (Simulation of Particles in A Radial Configuration) project has been successfully executed. This implementation models a spherical plasma composed of protons undergoing Coulomb explosion.

## Simulation Parameters

- Number of computational particles: 5,173 (initially 10,000, filtered to those within unit sphere)
- Simulation time: 1.0 (normalized units)
- Time step: 0.001
- Total iterations: 1,000
- Particle species: Protons
- Initial configuration: Particles uniformly distributed in a unit sphere (R = 1)

## Results

### Energy Conservation
- Initial energy: 10.530522
- Final energy: 10.532150
- Energy conservation error: 0.015457%

The excellent energy conservation demonstrates the numerical stability of the simulation.

### Particle Distribution
- Mean radial position: 1.6716
- Standard deviation of radial position: 0.4300
- Minimum radial position: 0.1328
- Maximum radial position: 2.2276

The particle distribution shows the expected expansion during the Coulomb explosion, with particles moving outward from the initial unit sphere.

## Output Files

1. `Coulomb_explosion_dt0p001.npy` (3.2 MB) - Complete simulation data including particle positions and velocities at each time step
2. `energy_vs_time.txt` (0.3 KB) - Tabulated energy values at each recorded time step
3. `energy_evolution.png` (125.1 KB) - Plot showing total energy evolution over time
4. `particle_analysis.png` (314.9 KB) - Analysis plots including particle positions and radial distribution

## Analysis

The simulation successfully demonstrates the Coulomb explosion phenomenon, where initially uniformly distributed protons in a sphere repel each other due to electrostatic forces, causing the sphere to expand over time. The energy conservation is excellent, indicating that the numerical methods used are stable and accurate.

The particle analysis shows that particles have moved significantly outward from their initial positions within the unit sphere, with the mean radial position increasing from approximately 0.5 (expected for a uniform distribution in a unit sphere) to 1.67, confirming the expansion process.