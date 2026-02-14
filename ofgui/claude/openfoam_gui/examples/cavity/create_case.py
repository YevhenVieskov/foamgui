"""
Lid-Driven Cavity Example Case
Classic validation case for incompressible flow
"""

CASE_METADATA = {
    'name': 'Lid-Driven Cavity',
    'solver': 'icoFoam',
    'description': 'Classic laminar flow validation case',
    'reynolds_number': 100,
    'domain': '0.1m x 0.1m square',
    'mesh_cells': 20 * 20,
    'time_step': 0.005,
    'end_time': 0.5,
    'typical_runtime': '~1 minute'
}

BLOCKMESH_DICT = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 0.1;

vertices
(
    (0 0 0)
    (1 0 0)
    (1 1 0)
    (0 1 0)
    (0 0 0.1)
    (1 0 0.1)
    (1 1 0.1)
    (0 1 0.1)
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    movingWall
    {
        type wall;
        faces
        (
            (3 7 6 2)
        );
    }
    fixedWalls
    {
        type wall;
        faces
        (
            (0 4 7 3)
            (2 6 5 1)
            (1 5 4 0)
        );
    }
    frontAndBack
    {
        type empty;
        faces
        (
            (0 3 2 1)
            (4 5 6 7)
        );
    }
);

mergePatchPairs
(
);

// ************************************************************************* //
"""

CONTROL_DICT = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     icoFoam;

startFrom       startTime;

startTime       0;

stopAt          endTime;

endTime         0.5;

deltaT          0.005;

writeControl    timeStep;

writeInterval   20;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

// ************************************************************************* //
"""

FV_SCHEMES = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
    grad(p)         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear orthogonal;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         orthogonal;
}

// ************************************************************************* //
"""

FV_SOLUTION = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-06;
        relTol          0.05;
    }

    pFinal
    {
        $p;
        relTol          0;
    }

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0;
    }
}

PISO
{
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}

// ************************************************************************* //
"""

INITIAL_U = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    location    "0";
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    movingWall
    {
        type            fixedValue;
        value           uniform (1 0 0);
    }
    fixedWalls
    {
        type            noSlip;
    }
    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
"""

INITIAL_P = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "0";
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    movingWall
    {
        type            zeroGradient;
    }
    fixedWalls
    {
        type            zeroGradient;
    }
    frontAndBack
    {
        type            empty;
    }
}

// ************************************************************************* //
"""

README = """# Lid-Driven Cavity Example

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
"""


def create_cavity_case(base_path):
    """Create complete cavity case structure"""
    from pathlib import Path
    
    case_path = Path(base_path) / 'cavity'
    
    # Create directory structure
    (case_path / '0').mkdir(parents=True, exist_ok=True)
    (case_path / 'constant').mkdir(exist_ok=True)
    (case_path / 'system').mkdir(exist_ok=True)
    
    # Write files
    with open(case_path / 'system' / 'blockMeshDict', 'w') as f:
        f.write(BLOCKMESH_DICT)
    
    with open(case_path / 'system' / 'controlDict', 'w') as f:
        f.write(CONTROL_DICT)
    
    with open(case_path / 'system' / 'fvSchemes', 'w') as f:
        f.write(FV_SCHEMES)
    
    with open(case_path / 'system' / 'fvSolution', 'w') as f:
        f.write(FV_SOLUTION)
    
    with open(case_path / '0' / 'U', 'w') as f:
        f.write(INITIAL_U)
    
    with open(case_path / '0' / 'p', 'w') as f:
        f.write(INITIAL_P)
    
    with open(case_path / 'README.md', 'w') as f:
        f.write(README)
    
    return case_path


if __name__ == '__main__':
    import sys
    base_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    case_path = create_cavity_case(base_path)
    print(f"Cavity case created at: {case_path}")
