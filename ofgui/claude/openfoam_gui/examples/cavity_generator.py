"""
Example Case Generator: Lid-Driven Cavity Flow
Classic CFD benchmark case
"""
from pathlib import Path
import shutil


class CavityCase:
    """Generate lid-driven cavity flow case"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.case_name = "cavity"
        self.case_path = self.output_dir / self.case_name
    
    def generate(self):
        """Generate complete cavity case"""
        print(f"Generating cavity case in {self.case_path}")
        
        # Create directory structure
        self._create_structure()
        
        # Generate files
        self._create_blockmesh_dict()
        self._create_control_dict()
        self._create_fv_schemes()
        self._create_fv_solution()
        self._create_transport_properties()
        self._create_turbulence_properties()
        self._create_boundary_conditions()
        self._create_readme()
        
        print(f"✓ Cavity case generated successfully")
        print(f"  Run: cd {self.case_path} && blockMesh && icoFoam")
    
    def _create_structure(self):
        """Create directory structure"""
        (self.case_path / '0').mkdir(parents=True, exist_ok=True)
        (self.case_path / 'constant').mkdir(exist_ok=True)
        (self.case_path / 'system').mkdir(exist_ok=True)
    
    def _create_blockmesh_dict(self):
        """Create blockMeshDict"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
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
        with open(self.case_path / 'system' / 'blockMeshDict', 'w') as f:
            f.write(content)
    
    def _create_control_dict(self):
        """Create controlDict"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
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
        with open(self.case_path / 'system' / 'controlDict', 'w') as f:
            f.write(content)
    
    def _create_fv_schemes(self):
        """Create fvSchemes"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
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
        with open(self.case_path / 'system' / 'fvSchemes', 'w') as f:
            f.write(content)
    
    def _create_fv_solution(self):
        """Create fvSolution"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
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
        with open(self.case_path / 'system' / 'fvSolution', 'w') as f:
            f.write(content)
    
    def _create_transport_properties(self):
        """Create transportProperties"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      transportProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

nu              [0 2 -1 0 0 0 0] 0.01;

// ************************************************************************* //
"""
        with open(self.case_path / 'constant' / 'transportProperties', 'w') as f:
            f.write(content)
    
    def _create_turbulence_properties(self):
        """Create turbulenceProperties"""
        content = """/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      turbulenceProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

simulationType laminar;

// ************************************************************************* //
"""
        with open(self.case_path / 'constant' / 'turbulenceProperties', 'w') as f:
            f.write(content)
    
    def _create_boundary_conditions(self):
        """Create initial and boundary conditions"""
        # U field
        u_content = """/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
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
        with open(self.case_path / '0' / 'U', 'w') as f:
            f.write(u_content)
        
        # p field
        p_content = """/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
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
        with open(self.case_path / '0' / 'p', 'w') as f:
            f.write(p_content)
    
    def _create_readme(self):
        """Create README file"""
        content = """# Lid-Driven Cavity Flow Example

## Description
Classic CFD benchmark case of a square cavity with moving top wall.

## Physical Setup
- Cavity: 0.1m x 0.1m
- Top wall velocity: 1 m/s (left to right)
- Kinematic viscosity: 0.01 m²/s
- Reynolds number: Re = 10

## Mesh
- 20 x 20 cells (400 cells total)
- Uniform orthogonal grid
- 2D simulation (1 cell thick in z-direction)

## Solver
- icoFoam (laminar, incompressible, transient)
- PISO algorithm
- Time step: 0.005 s
- End time: 0.5 s

## Running the Case

### Standard OpenFOAM
```bash
blockMesh
icoFoam
```

### With GUI
1. Open OpenFOAM GUI
2. File → Open Case
3. Select this directory
4. Mesh → Generate Mesh (blockMesh)
5. Solver → Run Solver
6. View results in Monitoring tab

## Expected Results
- Primary vortex forms in center
- Steady state reached around t=0.3s
- Maximum velocity at top wall: 1 m/s

## Post-Processing
```bash
paraFoam
```

Or use the GUI's contour viewer to visualize velocity and pressure fields.

## References
- Ghia, U., Ghia, K.N. and Shin, C.T. (1982)
  "High-Re solutions for incompressible flow using the Navier-Stokes equations"
  Journal of Computational Physics, 48, 387-411.
"""
        with open(self.case_path / 'README.md', 'w') as f:
            f.write(content)


def generate_cavity_example(output_dir: str = '.'):
    """Generate cavity flow example case
    
    Args:
        output_dir: Directory to create case in
    """
    case = CavityCase(output_dir)
    case.generate()
    return case.case_path


if __name__ == '__main__':
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    case_path = generate_cavity_example(output_dir)
    print(f"\nCavity case created at: {case_path}")
