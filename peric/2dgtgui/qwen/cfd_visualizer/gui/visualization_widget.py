"""
3D Visualization Widget - Star CCM+ Style
"""

from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox
from qtpy.QtCore import Signal, Slot
import pyvistaqt
import pyvista as pv
import numpy as np

class VisualizationWidget(QWidget):
    """3D visualization widget with Star CCM+ like features"""
    
    view_changed = Signal()
    
    def __init__(self):
        super().__init__()
        self.plotter = None
        self.current_data = None
        self.planes = []
        self.vectors_actor = None
        self.contour_actor = None
        self.streamline_actor = None
        
        self._setup_ui()
        self._setup_plotter()
    
    def _setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Control panel (Star CCM+ style)
        control_panel = QHBoxLayout()
        control_panel.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-bottom: 1px solid #cccccc;
                padding: 5px;
            }
        """)
        
        self.variable_combo = QComboBox()
        self.variable_combo.addItems(["Pressure", "Velocity", "Turbulent Energy"])
        self.variable_combo.setMinimumWidth(150)
        control_panel.addWidget(QLabel("Variable:"))
        control_panel.addWidget(self.variable_combo)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_view)
        control_panel.addWidget(refresh_btn)
        
        control_panel.addStretch()
        
        layout.addLayout(control_panel)
    
    def _setup_plotter(self):
        """Setup PyVista plotter"""
        self.plotter = pyvistaqt.QtInteractor(self)
        self.layout().addWidget(self.plotter.interactor)
        
        # Set Star CCM+ like style
        self.plotter.set_background('white')
        self.plotter.add_axes()
        self.plotter.add_orientation_widget()
        
        # Add lighting
        self.plotter.add_light()
    
    @Slot(dict)
    def update_data(self, data):
        """Update visualization with new data"""
        self.current_data = data
        self.plotter.clear()
        
        # Add mesh
        if 'mesh' in data:
            mesh = data['mesh']
            
            # Add contours
            self.contour_actor = self.plotter.add_mesh(
                mesh,
                scalars=data.get('scalars', 'Pressure'),
                cmap='viridis',
                opacity=0.8,
                show_edges=False,
                clim=data.get('clim', None)
            )
            
            # Add vectors if available
            if 'Velocity' in mesh.point_data:
                self.show_vectors(True)
        
        self.plotter.reset_camera()
        self.view_changed.emit()
    
    def show_vectors(self, show=True):
        """Show/hide vector field"""
        if self.vectors_actor:
            self.plotter.remove_actor(self.vectors_actor)
            self.vectors_actor = None
        
        if show and self.current_data and 'mesh' in self.current_data:
            mesh = self.current_data['mesh']
            
            if 'Velocity' in mesh.point_data:
                vectors = mesh['Velocity']
                
                self.vectors_actor = self.plotter.add_mesh(
                    mesh,
                    vectors=vectors,
                    color='red',
                    opacity=0.5,
                    glyph_factor=0.1,
                    glyph_resolution=8
                )
    
    def show_contours(self, show=True):
        """Show/hide contours"""
        if self.contour_actor:
            self.plotter.remove_actor(self.contour_actor)
            self.contour_actor = None
        
        if show and self.current_data and 'mesh' in self.current_data:
            mesh = self.current_data['mesh']
            self.contour_actor = self.plotter.add_mesh(
                mesh,
                scalars=self.current_data.get('scalars', 'Pressure'),
                cmap='viridis',
                opacity=0.8,
                show_edges=False
            )
    
    def show_streamlines(self, show=True):
        """Show/hide streamlines"""
        if self.streamline_actor:
            self.plotter.remove_actor(self.streamline_actor)
            self.streamline_actor = None
        
        if show and self.current_data and 'mesh' in self.current_data:
            mesh = self.current_data['mesh']
            
            if 'Velocity' in mesh.point_data:
                # Create streamlines
                streamlines = mesh.streamlines(
                    'Velocity',
                    start_position=(0, 0, 0),
                    n_points=100
                )
                
                self.streamline_actor = self.plotter.add_mesh(
                    streamlines,
                    color='blue',
                    line_width=2,
                    opacity=0.7
                )
    
    def add_plane_section(self, origin=None, normal=None):
        """Add plane section through the domain"""
        if not self.current_data or 'mesh' not in self.current_data:
            return
        
        mesh = self.current_data['mesh']
        
        # Default plane through center
        if origin is None:
            origin = mesh.center
        if normal is None:
            normal = [0, 0, 1]
        
        # Create plane
        plane = mesh.slice(origin=origin, normal=normal)
        
        # Add to plotter
        plane_actor = self.plotter.add_mesh(
            plane,
            scalars=self.current_data.get('scalars', 'Pressure'),
            cmap='plasma',
            opacity=1.0,
            show_edges=True
        )
        
        self.planes.append(plane_actor)
    
    def reset_camera(self):
        """Reset camera to default view"""
        self.plotter.reset_camera()
    
    def set_camera_view(self, view_type):
        """Set camera to preset view"""
        if view_type == "front":
            self.plotter.view_xy()
        elif view_type == "top":
            self.plotter.view_xz()
        elif view_type == "iso":
            self.plotter.view_isometric()
    
    def save_screenshot(self, filename):
        """Save current view as screenshot"""
        self.plotter.screenshot(filename)
    
    def _refresh_view(self):
        """Refresh the visualization"""
        if self.current_data:
            self.update_data(self.current_data)