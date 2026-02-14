"""
Example Case Generator: Flow Around Cylinder
Classic external flow case with vortex shedding
"""
from pathlib import Path
import math


class CylinderCase:
    """Generate flow around cylinder case"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.case_name = "cylinder"
        self.case_path = self.output_dir / self.case_name
        
        # Geometry parameters
        self.cylinder_radius = 0.05  # 5 cm
        self.domain_upstream = 0.5    # 50 cm upstream
        self.domain_downstream = 1.0  # 100 cm downstream
        self.domain_height = 0.4      # 40 cm domain height
        
        # Flow parameters
        self.velocity = 1.0  # m/s
        self.nu = 1.5e-5     # m²/s (air at 20°C)
    
    def generate(self):
        """Generate complete cylinder case"""
        print(f"Generating cylinder case in {self.case_path}")
        
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
        
        print(f"✓ Cylinder case generated successfully")
        print(f"  Run: cd {self.case_path} && blockMesh && pimpleFoam")
    
    def _create_structure(self):
        """Create directory structure"""
        (self.case_path / '0').mkdir(parents=True, exist_ok=True)
        (self.case_path / 'constant').mkdir(exist_ok=True)
        (self.case_path / 'system').mkdir(exist_ok=True)
    
    def _create_blockmesh_dict(self):
        """Create blockMeshDict with cylindrical geometry"""
        # Create mesh around cylinder using blocks
        r = self.cylinder_radius
        R = 0.2  # Outer radius for initial blocks
        
        # 45 degree angle points
        angle = math.pi / 4
        x1 = r * math.cos(angle)
        y1 = r * math.sin(angle)
        x2 = R * math.cos(angle)
        y2 = R * math.sin(angle)
        
        content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

vertices
(
    // Inner square around cylinder
    ({-x1} {-y1} 0)     // 0
    ({x1} {-y1} 0)      // 1
    ({x1} {y1} 0)       // 2
    ({-x1} {y1} 0)      // 3
    
    // Outer square
    ({-x2} {-y2} 0)     // 4
    ({x2} {-y2} 0)      // 5
    ({x2} {y2} 0)       // 6
    ({-x2} {y2} 0)      // 7
    
    // Upstream
    ({-self.domain_upstream} {-self.domain_height/2} 0)  // 8
    ({-self.domain_upstream} {self.domain_height/2} 0)   // 9
    
    // Downstream
    ({self.domain_downstream} {-self.domain_height/2} 0) // 10
    ({self.domain_downstream} {self.domain_height/2} 0)  // 11
    
    // Back plane (z = 0.1)
    ({-x1} {-y1} 0.1)   // 12
    ({x1} {-y1} 0.1)    // 13
    ({x1} {y1} 0.1)     // 14
    ({-x1} {y1} 0.1)    // 15
    
    ({-x2} {-y2} 0.1)   // 16
    ({x2} {-y2} 0.1)    // 17
    ({x2} {y2} 0.1)     // 18
    ({-x2} {y2} 0.1)    // 19
    
    ({-self.domain_upstream} {-self.domain_height/2} 0.1)  // 20
    ({-self.domain_upstream} {self.domain_height/2} 0.1)   // 21
    
    ({self.domain_downstream} {-self.domain_height/2} 0.1) // 22
    ({self.domain_downstream} {self.domain_height/2} 0.1)  // 23
);

blocks
(
    // Around cylinder
    hex (4 5 1 0 16 17 13 12) (20 20 1) simpleGrading (1 1 1)
    hex (5 6 2 1 17 18 14 13) (20 20 1) simpleGrading (1 1 1)
    hex (6 7 3 2 18 19 15 14) (20 20 1) simpleGrading (1 1 1)
    hex (7 4 0 3 19 16 12 15) (20 20 1) simpleGrading (1 1 1)
    
    // Upstream
    hex (8 4 7 9 20 16 19 21) (40 20 1) simpleGrading (1 1 1)
    
    // Downstream
    hex (5 10 11 6 17 22 23 18) (80 20 1) simpleGrading (1 1 1)
);

edges
(
    // Cylinder surface (inner)
    arc 0 1 ({r} 0 0)
    arc 1 2 (0 {r} 0)
    arc 2 3 ({-r} 0 0)
    arc 3 0 (0 {-r} 0)
    
    arc 12 13 ({r} 0 0.1)
    arc 13 14 (0 {r} 0.1)
    arc 14 15 ({-r} 0 0.1)
    arc 15 12 (0 {-r} 0.1)
    
    // Outer arcs
    arc 4 5 ({R} 0 0)
    arc 5 6 (0 {R} 0)
    arc 6 7 ({-R} 0 0)
    arc 7 4 (0 {-R} 0)
    
    arc 16 17 ({R} 0 0.1)
    arc 17 18 (0 {R} 0.1)
    arc 18 19 ({-R} 0 0.1)
    arc 19 16 (0 {-R} 0.1)
);

boundary
(
    inlet
    {{
        type patch;
        faces
        (
            (8 20 21 9)
        );
    }}
    
    outlet
    {{
        type patch;
        faces
        (
            (10 11 23 22)
        );
    }}
    
    cylinder
    {{
        type wall;
        faces
        (
            (0 12 13 1)
            (1 13 14 2)
            (2 14 15 3)
            (3 15 12 0)
        );
    }}
    
    top
    {{
        type symmetryPlane;
        faces
        (
            (9 21 19 7)
            (7 19 18 6)
            (6 18 23 11)
        );
    }}
    
    bottom
    {{
        type symmetryPlane;
        faces
        (
            (8 4 16 20)
            (4 5 17 16)
            (5 10 22 17)
        );
    }}
    
    frontAndBack
    {{
        type empty;
        faces
        (
            // Front (z=0)
            (0 1 5 4)
            (1 2 6 5)
            (2 3 7 6)
            (3 0 4 7)
            (4 7 9 8)
            (5 6 11 10)
            
            // Back (z=0.1)
            (12 16 17 13)
            (13 17 18 14)
            (14 18 19 15)
            (15 19 16 12)
            (16 20 21 19)
            (17 22 23 18)
        );
    }}
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

application     pimpleFoam;

startFrom       latestTime;

startTime       0;

stopAt          endTime;

endTime         10;

deltaT          0.001;

writeControl    adjustableRunTime;

writeInterval   0.1;

purgeWrite      0;

writeFormat     ascii;

writePrecision  6;

writeCompression off;

timeFormat      general;

timePrecision   6;

runTimeModifiable true;

adjustTimeStep  yes;

maxCo           1;

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
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwind grad(U);
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
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
        solver          GAMG;
        tolerance       1e-06;
        relTol          0.01;
        smoother        GaussSeidel;
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
        relTol          0.1;
    }

    UFinal
    {
        $U;
        relTol          0;
    }
}

PIMPLE
{
    nOuterCorrectors 1;
    nCorrectors      2;
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
        content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      transportProperties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

nu              [0 2 -1 0 0 0 0] {self.nu};

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
        u_content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform ({self.velocity} 0 0);

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform ({self.velocity} 0 0);
    }}

    outlet
    {{
        type            zeroGradient;
    }}

    cylinder
    {{
        type            noSlip;
    }}

    top
    {{
        type            symmetryPlane;
    }}

    bottom
    {{
        type            symmetryPlane;
    }}

    frontAndBack
    {{
        type            empty;
    }}
}}

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
    inlet
    {
        type            zeroGradient;
    }

    outlet
    {
        type            fixedValue;
        value           uniform 0;
    }

    cylinder
    {
        type            zeroGradient;
    }

    top
    {
        type            symmetryPlane;
    }

    bottom
    {
        type            symmetryPlane;
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
        Re = self.velocity * 2 * self.cylinder_radius / self.nu
        content = f"""# Flow Around Cylinder Example

## Description
Classic external flow case demonstrating vortex shedding behind a circular cylinder.

## Physical Setup
- Cylinder diameter: {2*self.cylinder_radius*100} cm
- Inlet velocity: {self.velocity} m/s
- Kinematic viscosity: {self.nu} m²/s (air at 20°C)
- Reynolds number: Re ≈ {Re:.0f}
- Domain: {self.domain_upstream}m upstream, {self.domain_downstream}m downstream

## Mesh
- Structured mesh with O-grid around cylinder
- Approximately 2000 cells
- 2D simulation (1 cell thick in z-direction)
- Refined mesh near cylinder surface

## Solver
- pimpleFoam (laminar, incompressible, transient)
- Adaptive time stepping (max Co = 1)
- PIMPLE algorithm
- Total simulation time: 10 seconds

## Expected Results
- Vortex street (Kármán vortex street) behind cylinder
- Periodic vortex shedding for Re > 40
- Strouhal number St ≈ 0.2 for Re = 100-200

## Running the Case

### Standard OpenFOAM
```bash
blockMesh
pimpleFoam
```

### With GUI
1. Open OpenFOAM GUI
2. File → Open Case
3. Select this directory
4. Mesh → Generate Mesh (blockMesh)
5. Solver → Run Solver
6. View vortex shedding in Monitoring tab

## Post-Processing
```bash
paraFoam
```

Or use the GUI's contour viewer to visualize:
- Velocity magnitude (vortex cores)
- Pressure distribution
- Vorticity

## Force Coefficients
To monitor lift and drag forces, add forceCoeffs function object to controlDict.

## References
- von Kármán, T. (1911) "Über den Mechanismus des Widerstandes, den ein bewegter Körper"
  Göttingen Nachrichten, Math.-Phys. Klasse, 509-517.
"""
        with open(self.case_path / 'README.md', 'w') as f:
            f.write(content)


def generate_cylinder_example(output_dir: str = '.'):
    """Generate cylinder flow example case
    
    Args:
        output_dir: Directory to create case in
    """
    case = CylinderCase(output_dir)
    case.generate()
    return case.case_path


if __name__ == '__main__':
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    case_path = generate_cylinder_example(output_dir)
    print(f"\nCylinder case created at: {case_path}")
