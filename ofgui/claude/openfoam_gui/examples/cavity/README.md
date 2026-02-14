# Lid-Driven Cavity Example

## Description
Classic validation case for laminar incompressible flow. A square cavity with the top wall moving at constant velocity, creating a characteristic vortex pattern.

## Problem Setup
- **Domain**: 0.1m x 0.1m square cavity
- **Reynolds Number**: 100
- **Top wall velocity**: 1 m/s
- **Fluid**: Incompressible, Newtonian
- **Flow regime**: Laminar

## Mesh
- **Cells**: 20 x 20 = 400 cells
- **Type**: Structured hexahedral
- **Quality**: Excellent (orthogonal)

## Solver Settings
- **Solver**: icoFoam (incompressible, laminar)
- **Time step**: 0.005 s
- **End time**: 0.5 s
- **Total steps**: 100

## Expected Results
- Primary vortex in center
- Secondary vortices in corners
- Velocity magnitude maximum at top wall
- Pressure driven by centrifugal effects

## Running the Case

### Using OpenFOAM GUI
1. File → Open Case → Select cavity directory
2. Mesh → Generate Mesh (blockMesh)
3. Solver → Run Solver

### Command Line
```bash
cd cavity
blockMesh
icoFoam
paraview cavity.foam  # Visualize results
```

## Post-Processing
- Velocity vectors show recirculation
- Streamlines reveal vortex structure
- Compare with Ghia et al. (1982) benchmark data

## Validation
This case is widely used for CFD code validation. Results should match published benchmarks for Re=100.

## References
- Ghia, U., Ghia, K.N., and Shin, C.T. (1982). "High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method". Journal of Computational Physics, 48(3), 387-411.

## Learning Points
- Basic mesh generation with blockMesh
- Setting boundary conditions
- Laminar flow patterns
- Vortex dynamics
- OpenFOAM case structure
