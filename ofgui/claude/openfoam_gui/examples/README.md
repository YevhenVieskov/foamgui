# OpenFOAM Example Cases

This directory contains fully-configured example cases demonstrating various OpenFOAM capabilities.

## Available Examples

### 1. Lid-Driven Cavity (`cavity/`)
- **Solver**: icoFoam (laminar incompressible)
- **Complexity**: Beginner
- **Runtime**: ~1 minute
- **Purpose**: CFD validation, learning blockMesh
- **Features**: 
  - Simple structured mesh
  - Classic benchmark case
  - Vortex flow patterns

### 2. Flow Around Cylinder (`cylinder/`)
- **Solver**: pimpleFoam (transient incompressible)
- **Complexity**: Intermediate
- **Runtime**: ~10 minutes
- **Purpose**: Vortex shedding, unsteady flow
- **Features**:
  - snappyHexMesh demonstration
  - Turbulent flow (Re=100-200)
  - Time-dependent phenomena
  - Karman vortex street

### 3. Airfoil (NACA0012) (`airfoil/`)
- **Solver**: simpleFoam (steady turbulent)
- **Complexity**: Advanced
- **Runtime**: ~30 minutes
- **Purpose**: Aerodynamics, lift/drag calculation
- **Features**:
  - Complex geometry
  - Turbulence modeling
  - Force coefficients
  - Boundary layer resolution

## Using Examples

### Method 1: OpenFOAM GUI
1. **File → Open Case**
2. Select example directory
3. **Mesh → Generate Mesh**
4. **Solver → Run Solver**
5. View results in Monitoring tab

### Method 2: Python Script
```python
from examples.cavity.create_case import create_cavity_case
case_path = create_cavity_case('/path/to/directory')
```

### Method 3: Command Line
```bash
cd cavity
python create_case.py
blockMesh
icoFoam
```

## Learning Path

1. **Start with Cavity** - Learn basics
2. **Progress to Cylinder** - Understand transient flows
3. **Master with Airfoil** - Complex geometries and turbulence

## Case Structure

Each example includes:
- `create_case.py` - Automated case setup
- `README.md` - Detailed documentation
- Complete OpenFOAM dictionaries
- Mesh generation scripts
- Post-processing instructions

## Validation

All examples are validated against:
- Published literature
- Experimental data
- OpenFOAM tutorial cases

## Customization

Modify these examples by:
- Changing Reynolds numbers
- Adjusting mesh resolution
- Trying different turbulence models
- Varying boundary conditions

See individual README files for specific details.
