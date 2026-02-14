"""
Real-time contour visualization widget
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QPushButton, QSlider, QCheckBox
)
from PyQt6.QtCore import QTimer, Qt
import pyvista as pv
from pyvistaqt import QtInteractor
import numpy as np
from pathlib import Path
import vtk


class ContourViewerWidget(QWidget):
    """Widget for real-time contour visualization"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.case_path = None
        self.monitoring = False
        self.current_mesh = None
        self.current_field = 'U'
        self.current_component = 'magnitude'
        self.current_time = None
        self.time_steps = []
        
        self._create_ui()
        
        # Setup monitoring timer
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._update_visualization)
    
    def _create_ui(self):
        """Create user interface"""
        layout = QVBoxLayout(self)
        
        # Controls
        controls = QHBoxLayout()
        
        # Field selection
        controls.addWidget(QLabel("Field:"))
        self.field_combo = QComboBox()
        self.field_combo.addItems(['U', 'p', 'T', 'k', 'epsilon', 'omega', 'nut'])
        self.field_combo.currentTextChanged.connect(self._on_field_changed)
        controls.addWidget(self.field_combo)
        
        # Component selection
        controls.addWidget(QLabel("Component:"))
        self.component_combo = QComboBox()
        self.component_combo.addItems(['magnitude', 'X', 'Y', 'Z'])
        self.component_combo.currentTextChanged.connect(self._on_component_changed)
        controls.addWidget(self.component_combo)
        
        # Time selection
        controls.addWidget(QLabel("Time:"))
        self.time_combo = QComboBox()
        self.time_combo.currentTextChanged.connect(self._on_time_changed)
        controls.addWidget(self.time_combo)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._load_time_steps)
        controls.addWidget(self.refresh_btn)
        
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Visualization controls
        viz_controls = QHBoxLayout()
        
        self.show_edges_check = QCheckBox("Show Edges")
        self.show_edges_check.stateChanged.connect(self._update_display_options)
        viz_controls.addWidget(self.show_edges_check)
        
        self.show_mesh_check = QCheckBox("Show Mesh")
        self.show_mesh_check.stateChanged.connect(self._update_display_options)
        viz_controls.addWidget(self.show_mesh_check)
        
        viz_controls.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setMaximumWidth(150)
        self.opacity_slider.valueChanged.connect(self._update_display_options)
        viz_controls.addWidget(self.opacity_slider)
        
        viz_controls.addStretch()
        
        layout.addLayout(viz_controls)
        
        # PyVista viewer
        self.plotter = QtInteractor(self)
        layout.addWidget(self.plotter.interactor)
        
        # View controls
        view_controls = QHBoxLayout()
        
        view_xy_btn = QPushButton("View XY")
        view_xy_btn.clicked.connect(lambda: self.plotter.view_xy())
        
        view_xz_btn = QPushButton("View XZ")
        view_xz_btn.clicked.connect(lambda: self.plotter.view_xz())
        
        view_yz_btn = QPushButton("View YZ")
        view_yz_btn.clicked.connect(lambda: self.plotter.view_yz())
        
        view_iso_btn = QPushButton("Isometric")
        view_iso_btn.clicked.connect(lambda: self.plotter.view_isometric())
        
        reset_btn = QPushButton("Reset Camera")
        reset_btn.clicked.connect(lambda: self.plotter.reset_camera())
        
        view_controls.addWidget(view_xy_btn)
        view_controls.addWidget(view_xz_btn)
        view_controls.addWidget(view_yz_btn)
        view_controls.addWidget(view_iso_btn)
        view_controls.addWidget(reset_btn)
        view_controls.addStretch()
        
        layout.addLayout(view_controls)
    
    def start_monitoring(self, case_path: str):
        """Start monitoring visualization"""
        self.case_path = Path(case_path)
        self.monitoring = True
        
        self._load_time_steps()
        
        interval = int(self.config.get('monitoring_interval', 1.0) * 1000)
        self.monitor_timer.start(interval)
    
    def stop_monitoring(self):
        """Stop monitoring visualization"""
        self.monitoring = False
        self.monitor_timer.stop()
    
    def _load_time_steps(self):
        """Load available time steps"""
        if not self.case_path:
            return
        
        self.time_steps = []
        
        # Find time directories
        for item in self.case_path.iterdir():
            if item.is_dir():
                try:
                    time_value = float(item.name)
                    self.time_steps.append(item.name)
                except ValueError:
                    continue
        
        # Sort time steps
        self.time_steps.sort(key=lambda x: float(x))
        
        # Update combo box
        current_time = self.time_combo.currentText()
        self.time_combo.clear()
        self.time_combo.addItems(self.time_steps)
        
        # Select latest time or restore previous selection
        if current_time in self.time_steps:
            self.time_combo.setCurrentText(current_time)
        elif self.time_steps:
            self.time_combo.setCurrentText(self.time_steps[-1])
    
    def _update_visualization(self):
        """Update visualization"""
        if not self.monitoring:
            return
        
        # Check for new time steps
        self._load_time_steps()
        
        # Update display if time changed
        if self.time_combo.currentText() != self.current_time:
            self._load_and_display()
    
    def _on_field_changed(self, field: str):
        """Handle field change"""
        self.current_field = field
        self._load_and_display()
    
    def _on_component_changed(self, component: str):
        """Handle component change"""
        self.current_component = component
        self._update_display_options()
    
    def _on_time_changed(self, time_str: str):
        """Handle time change"""
        if time_str:
            self.current_time = time_str
            self._load_and_display()
    
    def _load_and_display(self):
        """Load mesh and field data, then display"""
        if not self.case_path or not self.current_time:
            return
        
        try:
            # Load mesh
            mesh_file = self.case_path / 'constant' / 'polyMesh' / 'points'
            if not mesh_file.exists():
                # Try VTK output
                vtk_file = self.case_path / 'VTK' / f'{self.case_path.name}_{self.current_time}.vtk'
                if vtk_file.exists():
                    self.current_mesh = pv.read(str(vtk_file))
                else:
                    print("No mesh data found")
                    return
            else:
                # Parse OpenFOAM mesh
                self.current_mesh = self._load_openfoam_mesh()
            
            # Load field data
            self._load_field_data()
            
            # Display
            self._display_mesh()
            
        except Exception as e:
            print(f"Error loading visualization: {e}")
    
    def _load_openfoam_mesh(self):
        """Load OpenFOAM mesh (simplified)"""
        # This is a simplified loader - full implementation would need
        # proper OpenFOAM mesh parsing
        
        # For now, create a simple mesh
        # In production, use foamToVTK or similar converter
        
        mesh_file = self.case_path / 'constant' / 'polyMesh' / 'points'
        
        # Read points
        points = []
        with open(mesh_file, 'r') as f:
            in_points = False
            for line in f:
                if line.strip() == '(':
                    in_points = True
                    continue
                if in_points:
                    if line.strip() == ')':
                        break
                    # Parse point (x y z)
                    coords = line.strip('()
 ').split()
                    if len(coords) == 3:
                        points.append([float(x) for x in coords])
        
        if not points:
            return None
        
        points = np.array(points)
        
        # Create point cloud (cells would need face parsing)
        cloud = pv.PolyData(points)
        return cloud
    
    def _load_field_data(self):
        """Load field data for current time"""
        if not self.current_mesh:
            return
        
        time_dir = self.case_path / self.current_time
        field_file = time_dir / self.current_field
        
        if not field_file.exists():
            return
        
        # Parse field file (simplified)
        # In production, use proper OpenFOAM field parser
        
        try:
            values = []
            with open(field_file, 'r') as f:
                in_field = False
                for line in f:
                    if 'internalField' in line:
                        in_field = True
                        continue
                    if in_field:
                        if line.strip() == '(':
                            continue
                        if line.strip() == ')' or line.strip() == ');':
                            break
                        
                        # Try to parse value
                        value_str = line.strip('()
 ;')
                        if value_str:
                            if '(' in value_str:  # Vector
                                vector_parts = value_str.strip('()').split()
                                if len(vector_parts) == 3:
                                    values.append([float(x) for x in vector_parts])
                            else:  # Scalar
                                try:
                                    values.append(float(value_str))
                                except ValueError:
                                    pass
            
            if values:
                values = np.array(values)
                
                # Add to mesh
                if len(values.shape) == 1:  # Scalar
                    self.current_mesh[self.current_field] = values
                else:  # Vector
                    self.current_mesh[self.current_field] = values
                    # Add magnitude
                    magnitude = np.linalg.norm(values, axis=1)
                    self.current_mesh[f'{self.current_field}_magnitude'] = magnitude
        
        except Exception as e:
            print(f"Error loading field data: {e}")
    
    def _display_mesh(self):
        """Display mesh with current field"""
        self.plotter.clear()
        
        if not self.current_mesh:
            return
        
        # Determine scalar to display
        scalar_name = None
        if self.current_component == 'magnitude':
            scalar_name = f'{self.current_field}_magnitude'
            if scalar_name not in self.current_mesh.array_names:
                scalar_name = self.current_field
        else:
            # Component of vector field
            if self.current_field in self.current_mesh.array_names:
                field_data = self.current_mesh[self.current_field]
                if len(field_data.shape) > 1 and field_data.shape[1] >= 3:
                    component_idx = {'X': 0, 'Y': 1, 'Z': 2}[self.current_component]
                    scalar_name = f'{self.current_field}_{self.current_component}'
                    self.current_mesh[scalar_name] = field_data[:, component_idx]
        
        # Display options
        show_edges = self.show_edges_check.isChecked()
        show_mesh = self.show_mesh_check.isChecked()
        opacity = self.opacity_slider.value() / 100.0
        
        # Add mesh to plotter
        if scalar_name and scalar_name in self.current_mesh.array_names:
            self.plotter.add_mesh(
                self.current_mesh,
                scalars=scalar_name,
                show_edges=show_edges,
                opacity=opacity,
                cmap='jet'
            )
            self.plotter.add_scalar_bar(title=f'{self.current_field} ({self.current_component})')
        else:
            self.plotter.add_mesh(
                self.current_mesh,
                show_edges=True,
                color='lightgray',
                opacity=opacity
            )
        
        if show_mesh:
            self.plotter.add_mesh(self.current_mesh, style='wireframe', color='black', line_width=1)
        
        self.plotter.reset_camera()
    
    def _update_display_options(self):
        """Update display options"""
        if self.current_mesh:
            self._display_mesh()
