# File Descriptions

## Main Files

### `main.py`
Application entry point. Run this to start the GUI.

### `setup.py`
Package installation configuration. Used by pip.

### `requirements.txt`
Python package dependencies. Install with `pip install -r requirements.txt`

### `run_tests.sh`
Test runner script. Executes all unit and functional tests.

## Documentation

### `README.md`
Main documentation with features, installation, and usage guide.

### `INSTALL.md`
Detailed installation instructions for different platforms.

### `PROJECT_SUMMARY.md`
Complete project overview, architecture, and implementation details.

### `QUICK_START.md`
Quick reference for getting started in minutes.

### `LICENSE`
MIT License terms.

### `docs/DEVELOPER_GUIDE.md`
Developer documentation for contributors.

### `docs/API.md`
API reference documentation.

## Source Code (`src/`)

### `src/core/`
Core application logic

- `config.py`: Configuration management (AppConfig class)
- `case_manager.py`: OpenFOAM case operations (CaseManager class)
- `main_window.py`: Main application window

### `src/widgets/`
User interface components

- `blockmesh_editor.py`: Visual 3D blockMesh editor
- `solver_config.py`: Solver configuration interface
- `mesh_panel.py`: Mesh generation controls
- `residual_monitor.py`: Real-time residual plotting
- `contour_viewer.py`: 3D field visualization
- `case_tree.py`: Case file browser tree
- `new_case_dialog.py`: New case creation dialog

### `src/solvers/`
Solver definitions

- `solver_registry.py`: Database of solver metadata and validation

### `src/utils/`
Utility functions (future expansion)

## Tests (`tests/`)

### `tests/unit/test_core.py`
Unit tests for core functionality:
- Configuration management
- Case operations
- Solver registry
- Mesh generation
- Residual parsing

### `tests/functional/test_integration.py`
Integration tests for:
- Complete workflows
- Mesh generation
- Solver configuration
- GUI components
- Monitoring systems

## Configuration

### `~/.openfoam_gui/config.json`
User configuration file (created on first run):
- OpenFOAM installation path
- Default solver
- Mesh quality criteria
- UI preferences
- Auto-save settings

## Generated Files (Runtime)

### Case Structure
```
myCase/
├── 0/                  # Initial conditions
├── constant/           # Mesh and properties
│   └── polyMesh/      # Generated mesh
├── system/            # Solver settings
│   ├── controlDict
│   ├── fvSchemes
│   ├── fvSolution
│   └── blockMeshDict
└── log.*              # Solver output
```

## File Count Summary

- Python source files: 15
- Test files: 2
- Documentation files: 7
- Configuration files: 5
- Total: 29 files

All files are production-ready and fully documented.
