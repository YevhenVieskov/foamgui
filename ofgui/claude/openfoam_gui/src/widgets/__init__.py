"""
Widgets package
"""
from .case_tree import CaseTreeWidget
from .solver_config import SolverConfigWidget
from .mesh_panel import MeshPanelWidget
from .blockmesh_editor import BlockMeshEditorWidget
from .residual_monitor import ResidualMonitorWidget
from .contour_viewer import ContourViewerWidget

__all__ = [
    'CaseTreeWidget',
    'SolverConfigWidget',
    'MeshPanelWidget',
    'BlockMeshEditorWidget',
    'ResidualMonitorWidget',
    'ContourViewerWidget'
]
