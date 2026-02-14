# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Navigate to project
cd openfoam_gui

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python main.py
```

## First Case (10 minutes)

### Create New Case

1. **File → New Case**
2. Name: `myCavity`
3. Solver: `icoFoam`
4. Click OK

### Setup Mesh

1. **Mesh → blockMesh Editor**
2. Create 8 vertices for a unit cube:
   - (0,0,0), (1,0,0), (1,1,0), (0,1,0)
   - (0,0,1), (1,0,1), (1,1,1), (0,1,1)
3. Click "Add Block"
4. Set cells: 20 x 20 x 20
5. Click "Save blockMeshDict"
6. Click "Generate Mesh"

### Run Simulation

1. **Solver → Solver Configuration**
2. Set end time: 100
3. Set write interval: 10
4. Click Save
5. **Solver → Run Solver**
6. Switch to "Monitoring" tab
7. Watch residuals plot

## Project Structure

```
openfoam_gui/
├── main.py              # Run this
├── src/                 # Source code
├── tests/               # Tests
├── docs/                # Documentation
└── README.md            # Full documentation
```

## Key Features

- **Visual blockMesh Editor**: ICEM CFD-style 3D mesh editor
- **Solver Configuration**: Support for all major OpenFOAM solvers
- **Real-time Monitoring**: Live residual plots and contour visualization
- **Case Management**: Create, load, save cases easily

## Getting Help

- See `README.md` for full documentation
- See `INSTALL.md` for installation troubleshooting
- See `docs/DEVELOPER_GUIDE.md` for development info
- See `docs/API.md` for API reference

## Run Tests

```bash
./run_tests.sh
```

## Common Commands

```bash
# Run application
python main.py

# Run specific solver
# (configure through GUI)

# Run tests
./run_tests.sh

# Check installation
python -c "import PyQt6; import pyvista; print('OK')"
```

## Tips

1. **OpenFOAM Path**: Set in `~/.openfoam_gui/config.json`
2. **Auto-save**: Enabled by default (every 5 minutes)
3. **Recent Cases**: Access from File menu
4. **Keyboard Shortcuts**:
   - Ctrl+N: New case
   - Ctrl+O: Open case
   - Ctrl+S: Save case

Enjoy using OpenFOAM GUI!
