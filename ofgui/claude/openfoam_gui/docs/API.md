# API Documentation

## Core API

### AppConfig

```python
class AppConfig:
    """Application configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None)
    def get(self, key: str, default: Any = None) -> Any
    def set(self, key: str, value: Any) -> None
    def save() -> None
    def add_recent_case(self, case_path: str) -> None
```

### CaseManager

```python
class CaseManager:
    """Manages OpenFOAM cases"""
    
    def __init__(self, config: AppConfig)
    def create_case(self, case_data: Dict[str, Any]) -> Optional[str]
    def load_case(self, case_path: str) -> None
    def save_case(self, case_path: str) -> None
    def run_solver(self, case_path: str) -> None
    def stop_solver() -> None
    def run_mesher(self, case_path: str, mesher: str = 'blockMesh') -> None
```

### SolverRegistry

```python
class SolverRegistry:
    """Registry of OpenFOAM solvers"""
    
    def get_solver_list() -> List[str]
    def get_solver_info(self, solver_name: str) -> Dict[str, Any]
    def validate_solver_setup(self, solver_name: str, fields: List[str]) -> tuple[bool, List[str]]
```

## Widget API

### BlockMeshEditorWidget

```python
class BlockMeshEditorWidget(QMainWindow):
    """Visual blockMesh editor"""
    
    def __init__(self, case_path: str, config: AppConfig)
```

### ResidualMonitorWidget

```python
class ResidualMonitorWidget(QWidget):
    """Real-time residual monitoring"""
    
    def __init__(self, config: AppConfig, parent=None)
    def start_monitoring(self, case_path: str) -> None
    def stop_monitoring() -> None
```

### ContourViewerWidget

```python
class ContourViewerWidget(QWidget):
    """Real-time contour visualization"""
    
    def __init__(self, config: AppConfig, parent=None)
    def start_monitoring(self, case_path: str) -> None
    def stop_monitoring() -> None
```

For complete API documentation, see the source code docstrings.
