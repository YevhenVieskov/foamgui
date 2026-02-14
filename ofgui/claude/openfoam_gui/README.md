# OpenFOAM GUI - Star-CCM+ Style Interface

A comprehensive, professional-grade graphical user interface for OpenFOAM 2506, inspired by Star-CCM+. This application provides an intuitive, modern interface for CFD simulations with real-time monitoring, visual mesh editing, and comprehensive solver configuration.

## Features

### 🎨 Visual blockMesh Editor (ICEM CFD Style)
- **3D Interactive Editing**: Real-time 3D visualization of mesh blocks
- **Vertex Management**: Add, edit, and remove vertices visually
- **Block Definition**: Define hexahedral blocks with custom cell counts and grading
- **Boundary Conditions**: Visual boundary patch definition
- **Live Preview**: See your mesh structure as you build it
- **Export**: Generate blockMeshDict files automatically

### ⚙️ Comprehensive Solver Configuration
- **All Major Solvers**: Support for simpleFoam, pimpleFoam, icoFoam, interFoam, buoyantSimpleFoam, and more
- **Field Validation**: Automatic validation of required fields for each solver
- **Turbulence Models**: Full support for RANS and LES turbulence models
- **Discretization Schemes**: Configure all discretization schemes visually
- **Solution Settings**: Control solver parameters, tolerances, and algorithms
- **Validation**: Real-time checking of solver setup requirements

### 🔧 Mesh Generation Tools
- **blockMesh**: Visual editor with 3D preview
- **snappyHexMesh**: Guided setup wizard
- **cfMesh**: Configuration interface
- **Quality Checks**: Automatic mesh quality assessment
- **One-Click Generation**: Run meshers directly from the GUI

### 📊 Real-Time Monitoring
- **Residual Plots**: Live plotting of all field residuals
  - Multiple field display
  - Logarithmic scaling
  - Customizable history length
  - Auto-scaling options
  
- **Contour Visualization**: Real-time field visualization
  - Multiple field types (U, p, T, k, epsilon, omega)
  - Component selection (magnitude, X, Y, Z)
  - Interactive 3D rendering
  - Time step navigation
  - Adjustable opacity and display options

### 📁 Case Management
- **Project Structure**: Standard OpenFOAM case organization
- **Recent Cases**: Quick access to recently opened cases
- **Templates**: Create cases from templates
- **Auto-Save**: Automatic case saving
- **Case Validation**: Verify case structure integrity

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenFOAM 2506 or compatible version
- Linux, macOS, or Windows with WSL

### Install via pip

```bash
# Clone the repository
git clone https://github.com/yourusername/openfoam-gui.git
cd openfoam-gui

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/openfoam-gui.git
cd openfoam-gui

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install PyQt6 pyvista pyvistaqt vtk numpy matplotlib scipy

# Run the application
python main.py
```

## Quick Start

### Launch the Application

```bash
# If installed via pip
openfoam-gui

# Or run directly
python main.py
```

### Create a New Case

1. **File → New Case**
2. Enter case name and location
3. Select solver type
4. Click OK

### Configure the Mesh

1. **Mesh → blockMesh Editor**
2. Add vertices by clicking "Add Vertex"
3. Create blocks from vertices
4. Define boundary conditions
5. Save blockMeshDict
6. Click "Generate Mesh"

### Configure the Solver

1. Select **Solver Setup** tab
2. Choose your solver from the dropdown
3. Configure discretization schemes
4. Set solution parameters
5. Save configuration

### Run Simulation

1. **Solver → Run Solver**
2. Monitor progress in **Monitoring** tab
3. Watch residuals in real-time
4. View field contours as they develop

## Usage Guide

### blockMesh Visual Editor

The blockMesh editor provides an ICEM CFD-style interface for creating structured hexahedral meshes:

#### Adding Vertices
```python
# Vertices are defined by X, Y, Z coordinates
# Click "Add Vertex" and enter coordinates in the table
# Example: (0, 0, 0), (1, 0, 0), (1, 1, 0), etc.
```

#### Creating Blocks
```python
# Blocks are defined by 8 vertices in OpenFOAM order
# Select vertices: 0-3 (bottom face), 4-7 (top face)
# Specify cell count: (nx, ny, nz)
# Define grading: (gx, gy, gz) for cell size distribution
```

#### Mesh Grading
- **Value = 1**: Uniform cell spacing
- **Value > 1**: Cells grow in positive direction
- **Value < 1**: Cells shrink in positive direction

### Solver Configuration

#### Field Requirements by Solver

**simpleFoam** (Steady-state incompressible):
- Required: U, p
- Optional: k, epsilon, omega, nut

**pimpleFoam** (Transient incompressible):
- Required: U, p
- Optional: k, epsilon, omega, nut

**interFoam** (Two-phase):
- Required: U, p, alpha.water
- Optional: k, epsilon, omega

**buoyantSimpleFoam** (Buoyancy-driven):
- Required: U, p, T
- Optional: k, epsilon, omega, nut

### Real-Time Monitoring

#### Residual Plots
- **Auto Scale**: Automatically adjust y-axis limits
- **Log Scale**: View residuals on logarithmic scale
- **History**: Control how many iterations to display
- **Field Selection**: Toggle visibility of individual fields

#### Contour Visualization
- **Field**: Select which field to visualize (U, p, T, etc.)
- **Component**: Choose magnitude or individual components (X, Y, Z)
- **Time**: Navigate through different time steps
- **Display Options**: Toggle edges, mesh wireframe, adjust opacity

## Testing

The application includes comprehensive unit and functional tests:

### Run All Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test suite
python -m pytest tests/unit/
python -m pytest tests/functional/
```

### Unit Tests

```bash
# Test core functionality
python tests/unit/test_core.py

# Expected output:
# test_config_creation (test_core.TestAppConfig) ... ok
# test_config_get_set (test_core.TestAppConfig) ... ok
# test_config_persistence (test_core.TestAppConfig) ... ok
# ...
```

### Functional Tests

```bash
# Test integration and workflows
python tests/functional/test_integration.py

# Expected output:
# test_complete_workflow (test_integration.TestCaseWorkflow) ... ok
# test_blockmesh_dict_creation (test_integration.TestMeshGeneration) ... ok
# test_solver_field_validation (test_integration.TestSolverConfiguration) ... ok
# ...
```

## Architecture

### Project Structure

```
openfoam_gui/
├── main.py                 # Application entry point
├── src/
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration management
│   │   ├── case_manager.py # Case operations
│   │   └── main_window.py # Main application window
│   ├── widgets/           # UI widgets
│   │   ├── blockmesh_editor.py    # Visual blockMesh editor
│   │   ├── solver_config.py       # Solver configuration
│   │   ├── mesh_panel.py          # Mesh generation panel
│   │   ├── residual_monitor.py    # Residual plotting
│   │   ├── contour_viewer.py      # Field visualization
│   │   ├── case_tree.py           # Case file browser
│   │   └── new_case_dialog.py     # New case wizard
│   ├── solvers/           # Solver definitions
│   │   └── solver_registry.py     # Solver database
│   └── utils/             # Utilities
├── tests/
│   ├── unit/              # Unit tests
│   │   └── test_core.py
│   └── functional/        # Integration tests
│       └── test_integration.py
├── resources/             # Icons, templates, etc.
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup
└── README.md             # This file
```

### Key Components

#### Core Classes

- **AppConfig**: Manages application configuration and settings
- **CaseManager**: Handles OpenFOAM case operations (create, load, save, run)
- **SolverRegistry**: Database of solver definitions and requirements

#### Widgets

- **MainWindow**: Primary application window with menu, toolbar, and tabs
- **BlockMeshEditorWidget**: Visual 3D editor for blockMesh
- **SolverConfigWidget**: Comprehensive solver configuration interface
- **ResidualMonitorWidget**: Real-time residual plotting with matplotlib
- **ContourViewerWidget**: 3D field visualization with PyVista

## Configuration

### Application Settings

Settings are stored in `~/.openfoam_gui/config.json`:

```json
{
  "openfoam_path": "/opt/openfoam2506",
  "default_solver": "simpleFoam",
  "mesh_quality_criteria": {
    "maxNonOrtho": 70,
    "maxBoundarySkewness": 20,
    "maxInternalSkewness": 4
  },
  "theme": "dark",
  "auto_save": true,
  "auto_save_interval": 300,
  "real_time_monitoring": true,
  "monitoring_interval": 1.0,
  "plot_history_length": 1000
}
```

### OpenFOAM Path

Set your OpenFOAM installation path in the configuration file or via the GUI:
- **Settings → Preferences → OpenFOAM Path**

## Supported Solvers

### Incompressible Flow
- **simpleFoam**: Steady-state, turbulent flow
- **pimpleFoam**: Transient, turbulent flow
- **icoFoam**: Transient, laminar flow
- **pisoFoam**: Transient flow

### Multiphase Flow
- **interFoam**: Two-phase, immiscible fluids
- **multiphaseInterFoam**: Multiple phases

### Heat Transfer
- **buoyantSimpleFoam**: Steady buoyancy-driven flow
- **buoyantPimpleFoam**: Transient buoyancy-driven flow

### Compressible Flow
- **rhoSimpleFoam**: Steady compressible flow
- **rhoPimpleFoam**: Transient compressible flow
- **sonicFoam**: Transient compressible flow

## Troubleshooting

### Common Issues

**Issue**: "OpenFOAM not found"
- **Solution**: Set correct OpenFOAM path in configuration

**Issue**: "Cannot generate mesh"
- **Solution**: Ensure blockMeshDict is valid and case structure is correct

**Issue**: "Residuals not updating"
- **Solution**: Check that solver is running and log file is being written

**Issue**: "PyVista display issues"
- **Solution**: Update graphics drivers, ensure OpenGL support

### Debug Mode

Enable debug logging:

```bash
export OPENFOAM_GUI_DEBUG=1
python main.py
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document all public APIs
- Write comprehensive docstrings

### Running Tests Before Commit

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Run tests
pytest tests/ --cov=src

# Type checking
mypy src/
```

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- OpenFOAM Foundation for the excellent CFD toolkit
- PyVista team for the powerful 3D visualization library
- Qt/PyQt team for the robust GUI framework
- Star-CCM+ for interface design inspiration

## Contact

- **Issues**: https://github.com/yourusername/openfoam-gui/issues
- **Discussions**: https://github.com/yourusername/openfoam-gui/discussions

## Roadmap

### Version 1.1 (Planned)
- [ ] Parallel processing support
- [ ] Advanced mesh quality checks
- [ ] Custom solver definitions
- [ ] Batch case generation
- [ ] Results export (VTK, CSV)

### Version 1.2 (Planned)
- [ ] Plugin system
- [ ] Custom post-processing scripts
- [ ] Remote case execution
- [ ] Cloud storage integration
- [ ] Advanced visualization (iso-surfaces, streamlines)

### Version 2.0 (Future)
- [ ] Machine learning-based mesh optimization
- [ ] Automated solver selection
- [ ] Collaborative features
- [ ] Web-based interface option
