# Component Architecture Deep Dive

This guide explains how each component of the OpenFOAM GUI works internally.

## Table of Contents
1. [Configuration System](#configuration-system)
2. [Case Management](#case-management)
3. [Visual blockMesh Editor](#visual-blockmesh-editor)
4. [Real-Time Monitoring](#real-time-monitoring)
5. [Solver Registry](#solver-registry)
6. [Mesh Quality Checker](#mesh-quality-checker)

---

## Configuration System

### Architecture
The configuration system (`src/core/config.py`) uses a simple JSON-based persistence layer with in-memory caching.

### How It Works

```python
class AppConfig:
    def __init__(self, config_file: Optional[str] = None):
        # 1. Determine config file location
        self.config_file = config_file or self._get_default_config_path()
        
        # 2. Load or create default config
        self.config = self._load_config()
```

**Key Design Decisions:**
- **JSON over pickle**: Human-readable, version-control friendly
- **Lazy loading**: Config loaded only when accessed
- **Atomic writes**: Prevents corruption during save
- **Default values**: Ensures app runs even without config file

### Data Flow

```
User Action → GUI Widget → config.set(key, value)
                              ↓
                         In-memory dict update
                              ↓
                         config.save()
                              ↓
                         JSON file written
```

### Example: Adding Recent Case

```python
def add_recent_case(self, case_path: str):
    # 1. Get current list
    recent = self.config.get('recent_cases', [])
    
    # 2. Remove if already exists (prevent duplicates)
    if case_path in recent:
        recent.remove(case_path)
    
    # 3. Add to front (most recent first)
    recent.insert(0, case_path)
    
    # 4. Limit list size
    recent = recent[:self.config.get('max_recent_cases', 10)]
    
    # 5. Save atomically
    self.set('recent_cases', recent)
```

---

## Case Management

### Architecture
The `CaseManager` (`src/core/case_manager.py`) orchestrates all OpenFOAM case operations.

### Case Creation Flow

```
create_case(case_data)
    ↓
Create directory structure
    ├── constant/
    │   └── polyMesh/
    ├── system/
    │   ├── controlDict
    │   ├── fvSchemes
    │   └── fvSolution
    └── 0/
        ├── U
        ├── p
        └── (other fields)
    ↓
Generate dictionaries from templates
    ↓
Return case path
```

### Dictionary Generation

The system uses Python string templates:

```python
def _create_control_dict(self, case_path: Path, case_data: Dict):
    control_dict = f"""
    FoamFile {{ version 2.0; ... }}
    
    application     {case_data['solver']};
    startTime       0;
    endTime         1000;
    deltaT          1;
    """
    
    with open(case_path / 'system' / 'controlDict', 'w') as f:
        f.write(control_dict)
```

**Why templates?** 
- Simple and maintainable
- Easy to customize
- No external dependencies

### Solver Execution

```python
def run_solver(self, case_path: str):
    # 1. Source OpenFOAM environment
    openfoam_path = self.config.get('openfoam_path')
    
    # 2. Build command
    cmd = f'''
        cd {case_path} && \
        source {openfoam_path}/etc/bashrc && \
        {solver} > log.{solver} 2>&1
    '''
    
    # 3. Run asynchronously
    self.solver_process = subprocess.Popen(
        cmd, shell=True, executable='/bin/bash'
    )
```

**Key Points:**
- Subprocess allows non-blocking execution
- Output redirected to log file
- Environment sourced per execution

---

## Visual blockMesh Editor

### Architecture Overview

The blockMesh editor combines PyVista for 3D visualization with PyQt for UI controls.

```
┌─────────────────────────────────────────┐
│          BlockMeshEditorWidget          │
├──────────────────┬──────────────────────┤
│  Control Panel   │   3D Viewer (PyVista)│
│  ┌────────────┐  │   ┌────────────────┐ │
│  │ Vertices   │  │   │                │ │
│  │ Table      │  │   │   Interactive  │ │
│  ├────────────┤  │   │   3D View      │ │
│  │ Blocks     │  │   │                │ │
│  │ Table      │  │   │   - Vertices   │ │
│  ├────────────┤  │   │   - Blocks     │ │
│  │ Boundaries │  │   │   - Labels     │ │
│  └────────────┘  │   └────────────────┘ │
└──────────────────┴──────────────────────┘
```

### Data Model

```python
class BlockMeshEditorWidget:
    def __init__(self):
        self.vertices = []  # List of [x, y, z] coordinates
        self.blocks = []    # List of block definitions
        self.edges = []     # Edge specifications
        self.boundaries = [] # Boundary patches
```

### Vertex Management

```python
def _add_vertex(self):
    # 1. Create vertex at origin
    vertex = [0.0, 0.0, 0.0]
    self.vertices.append(vertex)
    
    # 2. Add to table
    row = self.vertices_table.rowCount()
    self.vertices_table.insertRow(row)
    self.vertices_table.setItem(row, 0, QTableWidgetItem(str(row)))
    
    # 3. Update 3D view
    self._update_viewer()
```

### 3D Visualization Pipeline

```python
def _update_viewer(self):
    # 1. Clear previous visualization
    self.plotter.clear()
    
    # 2. Plot vertices as spheres
    if self.vertices:
        vertices_array = np.array(self.vertices)
        self.plotter.add_points(
            vertices_array,
            color='red',
            point_size=10,
            render_points_as_spheres=True
        )
    
    # 3. Plot blocks as hexahedra
    for block in self.blocks:
        points = np.array([self.vertices[i] for i in block['vertices']])
        
        # Define hexahedron faces (counterclockwise)
        faces = np.array([
            [4, 0, 1, 2, 3],  # bottom
            [4, 4, 5, 6, 7],  # top
            [4, 0, 1, 5, 4],  # front
            # ... other faces
        ])
        
        mesh = pv.PolyData(points, faces)
        self.plotter.add_mesh(
            mesh,
            color='lightblue',
            opacity=0.3,
            show_edges=True
        )
    
    # 4. Add axes
    self.plotter.add_axes()
    self.plotter.reset_camera()
```

### blockMeshDict Generation

```python
def _generate_blockmesh_dict(self) -> str:
    # 1. Generate vertices section
    vertices_str = "(\n"
    for v in self.vertices:
        vertices_str += f"    ({v[0]} {v[1]} {v[2]})\n"
    vertices_str += ")"
    
    # 2. Generate blocks section
    blocks_str = "(\n"
    for block in self.blocks:
        vertices = ' '.join(map(str, block['vertices']))
        cells = block['cells']
        grading = block['grading']
        blocks_str += f"    hex ({vertices}) "
        blocks_str += f"({cells[0]} {cells[1]} {cells[2]}) "
        blocks_str += f"simpleGrading ({grading[0]} {grading[1]} {grading[2]})\n"
    blocks_str += ")"
    
    # 3. Assemble complete dictionary
    return TEMPLATE.format(
        vertices=vertices_str,
        blocks=blocks_str,
        boundaries=boundaries_str
    )
```

---

## Real-Time Monitoring

### Residual Monitor Architecture

```
Log File → Parser → Data Model → matplotlib → Display
   ↓          ↓          ↓            ↓           ↓
log.solver  regex    residuals{}   figure    QWidget
           patterns   iterations    canvas
```

### Parsing Pipeline

```python
def _parse_residuals(self, lines: list):
    current_time = None
    
    for line in lines:
        # 1. Detect time step
        time_match = re.search(r'Time\s*=\s*(\d+\.?\d*)', line)
        if time_match:
            current_time = float(time_match.group(1))
            continue
        
        # 2. Extract residual
        residual_match = re.search(
            r'Solving for (\w+),.*Initial residual = ([\d.e+-]+)',
            line
        )
        
        if residual_match:
            field = residual_match.group(1)
            residual = float(residual_match.group(2))
            
            # 3. Store in data structure
            self.residuals[field].append(residual)
            
            # 4. Maintain sync with iterations
            while len(self.residuals[field]) < len(self.iterations):
                self.residuals[field].append(None)
```

### Update Mechanism

```python
# QTimer triggers periodic updates
self.monitor_timer = QTimer()
self.monitor_timer.timeout.connect(self._update_residuals)
self.monitor_timer.start(interval)  # milliseconds

def _update_residuals(self):
    # 1. Read log file
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # 2. Parse new data
    self._parse_residuals(lines)
    
    # 3. Update plot
    self._update_plot()
```

### Matplotlib Integration

```python
def _update_plot(self):
    self.ax.clear()
    
    # Plot each field with different color
    colors = plt.cm.tab10(np.linspace(0, 1, 10))
    
    for i, (field, values) in enumerate(self.residuals.items()):
        if self.field_checks[field].isChecked():
            self.ax.plot(
                self.iterations,
                values,
                '-o',
                label=field,
                color=colors[i],
                markersize=3
            )
    
    # Formatting
    self.ax.set_yscale('log')
    self.ax.set_xlabel('Iteration')
    self.ax.set_ylabel('Residual')
    self.ax.legend()
    self.ax.grid(True)
    
    # Redraw canvas
    self.canvas.draw()
```

---

## Solver Registry

### Design Pattern: Registry

The solver registry uses the **Registry Pattern** to maintain a centralized database of solver metadata.

```python
class ExtendedSolverRegistry:
    def __init__(self):
        # Load all solver definitions into memory
        self.solvers = self._load_all_solvers()
    
    def _load_all_solvers(self) -> Dict[str, Any]:
        return {
            'simpleFoam': {
                'description': '...',
                'required_fields': ['U', 'p'],
                'turbulence_models': [...],
                'category': 'Incompressible'
            },
            # ... 40+ other solvers
        }
```

### Validation Logic

```python
def validate_solver_setup(self, solver_name: str, fields: List[str]):
    # 1. Get solver requirements
    solver_info = self.solvers.get(solver_name, {})
    required = solver_info.get('required_fields', [])
    
    # 2. Check for missing fields
    missing = [f for f in required if f not in fields]
    
    # 3. Return validation result
    return len(missing) == 0, missing
```

**Usage:**
```python
registry = ExtendedSolverRegistry()
is_valid, missing = registry.validate_solver_setup('simpleFoam', ['U', 'p'])
if not is_valid:
    print(f"Missing fields: {missing}")
```

### Search Functionality

```python
def search_solvers(self, query: str) -> List[str]:
    query = query.lower()
    results = []
    
    for name, info in self.solvers.items():
        # Search in multiple fields
        if (query in name.lower() or
            query in info['description'].lower() or
            any(query in app.lower() 
                for app in info['typical_applications'])):
            results.append(name)
    
    return results
```

---

## Mesh Quality Checker

### Quality Assessment Pipeline

```
OpenFOAM checkMesh → stdout → Parser → Metrics → Assessment → Report
         ↓              ↓        ↓         ↓          ↓          ↓
    subprocess      regex    dict()    compare   grading    string
```

### Running checkMesh

```python
def run_check_mesh(self):
    # 1. Execute checkMesh utility
    result = subprocess.run(
        ['checkMesh', '-case', str(self.case_path)],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # 2. Parse output
    self._parse_checkmesh_output(result.stdout)
    
    return self.mesh_stats
```

### Parsing Strategy

```python
def _parse_checkmesh_output(self, output: str):
    # Use regex to extract metrics
    
    # Example: "Max non-orthogonality = 45.5 average = 15.2"
    match = re.search(
        r'Max non-orthogonality = ([\d.]+) average = ([\d.]+)',
        output
    )
    if match:
        self.mesh_stats['non_orthogonality'] = {
            'max': float(match.group(1)),
            'average': float(match.group(2))
        }
```

### Quality Grading

```python
def assess_quality(self):
    non_ortho = self.mesh_stats['non_orthogonality']['max']
    
    # Compare against quality criteria
    if non_ortho <= CRITERIA['excellent']['maxNonOrtho']:
        grade = 'excellent'
    elif non_ortho <= CRITERIA['good']['maxNonOrtho']:
        grade = 'good'
    elif non_ortho <= CRITERIA['acceptable']['maxNonOrtho']:
        grade = 'acceptable'
    else:
        grade = 'poor'
    
    return {'overall_grade': grade, ...}
```

### Report Generation

```python
def generate_quality_report(self) -> str:
    template = """
    ╔══════════════════════════════════════╗
    ║     MESH QUALITY ASSESSMENT          ║
    ╚══════════════════════════════════════╝
    
    Cells:              {cells}
    Non-Orthogonality:  {non_ortho_max:.2f} ({grade})
    
    {issues}
    {recommendations}
    """
    
    return template.format(**self.mesh_stats, **assessment)
```

---

## Performance Optimizations

### Lazy Loading
Components are only initialized when first accessed:
```python
@property
def solver_registry(self):
    if not hasattr(self, '_registry'):
        self._registry = ExtendedSolverRegistry()
    return self._registry
```

### Caching
Expensive operations are cached:
```python
@lru_cache(maxsize=128)
def get_solver_info(self, solver_name: str):
    return self.solvers.get(solver_name, {})
```

### Asynchronous Operations
Long-running tasks use separate threads/processes:
```python
self.solver_process = subprocess.Popen(...)  # Non-blocking
```

---

## Testing Strategy

Each component has dedicated tests:

1. **Unit Tests**: Individual methods
2. **Integration Tests**: Component interactions
3. **GUI Tests**: User interface automation
4. **Performance Tests**: Speed and memory

Example:
```python
def test_config_persistence(self):
    # 1. Create and save
    config = AppConfig(file_path)
    config.set('key', 'value')
    
    # 2. Reload and verify
    config2 = AppConfig(file_path)
    assert config2.get('key') == 'value'
```

---

## Further Reading

- **PyQt6 Documentation**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **PyVista Documentation**: https://docs.pyvista.org/
- **OpenFOAM User Guide**: https://www.openfoam.com/documentation/user-guide

For questions or contributions, see CONTRIBUTING.md
