"""
CAFFA GUI - Star CCM+ like interface for CAFFA CFD results
Built with PyQt5, PyVista, and VTK

This is the main GUI application providing interactive 3D visualization
of CAFFA computational fluid dynamics results.
"""
import sys
import numpy as np
from typing import Optional, List

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QComboBox, QLabel, QSlider, QGroupBox, QFileDialog,
        QMenuBar, QMenu, QAction, QDockWidget, QCheckBox, QSpinBox,
        QDoubleSpinBox, QTabWidget, QTextEdit, QSplitter
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QTimer
    from PyQt5.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    print("Warning: PyQt5 not available. GUI cannot be created.")
    PYQT_AVAILABLE = False

try:
    import pyvista as pv
    from pyvista.plotting.qt_plotting import QtInteractor
    PYVISTA_AVAILABLE = True
except ImportError:
    print("Warning: PyVista not available. 3D visualization disabled.")
    PYVISTA_AVAILABLE = False

from caffa_reader import CAFFAReader, CAFFAData, create_sample_data


class CAFFAVisualizer(QMainWindow):
    """Main window for CAFFA visualization"""
    
    def __init__(self):
        super().__init__()
        
        self.reader = CAFFAReader()
        self.current_data: Optional[CAFFAData] = None
        self.mesh = None
        self.current_field = 'velocity_magnitude'
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('CAFFA CFD Viewer - Star CCM+ Style')
        self.setGeometry(100, 100, 1600, 900)
        
        # Create menu bar
        self.create_menus()
        
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - controls
        left_panel = self.create_control_panel()
        splitter.addWidget(left_panel)
        
        # Center - 3D viewer
        self.viewer_widget = self.create_viewer_widget()
        splitter.addWidget(self.viewer_widget)
        
        # Right panel - information
        right_panel = self.create_info_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (20% - 60% - 20%)
        splitter.setSizes([300, 1000, 300])
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
    def create_menus(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open Result File...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        load_sample_action = QAction('Load Sample Data', self)
        load_sample_action.triggered.connect(self.load_sample_data)
        file_menu.addAction(load_sample_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('Export Screenshot...', self)
        export_action.setShortcut('Ctrl+S')
        export_action.triggered.connect(self.export_screenshot)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        reset_camera_action = QAction('Reset Camera', self)
        reset_camera_action.setShortcut('R')
        reset_camera_action.triggered.connect(self.reset_camera)
        view_menu.addAction(reset_camera_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        calc_action = QAction('Field Calculator...', self)
        calc_action.triggered.connect(self.show_field_calculator)
        tools_menu.addAction(calc_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_control_panel(self) -> QWidget:
        """Create left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Field selection
        field_group = QGroupBox("Field Selection")
        field_layout = QVBoxLayout()
        
        self.field_combo = QComboBox()
        self.field_combo.addItems([
            'Velocity Magnitude',
            'U Velocity',
            'V Velocity',
            'Pressure',
            'Temperature',
            'Turbulent Kinetic Energy',
            'Dissipation'
        ])
        self.field_combo.currentTextChanged.connect(self.on_field_changed)
        field_layout.addWidget(QLabel("Variable:"))
        field_layout.addWidget(self.field_combo)
        
        field_group.setLayout(field_layout)
        layout.addWidget(field_group)
        
        # Visualization options
        vis_group = QGroupBox("Visualization")
        vis_layout = QVBoxLayout()
        
        self.show_mesh_cb = QCheckBox("Show Mesh")
        self.show_mesh_cb.setChecked(False)
        self.show_mesh_cb.stateChanged.connect(self.update_visualization)
        vis_layout.addWidget(self.show_mesh_cb)
        
        self.show_contours_cb = QCheckBox("Show Contours")
        self.show_contours_cb.setChecked(True)
        self.show_contours_cb.stateChanged.connect(self.update_visualization)
        vis_layout.addWidget(self.show_contours_cb)
        
        self.show_vectors_cb = QCheckBox("Show Vectors")
        self.show_vectors_cb.setChecked(False)
        self.show_vectors_cb.stateChanged.connect(self.update_visualization)
        vis_layout.addWidget(self.show_vectors_cb)
        
        self.show_streamlines_cb = QCheckBox("Show Streamlines")
        self.show_streamlines_cb.setChecked(False)
        self.show_streamlines_cb.stateChanged.connect(self.update_visualization)
        vis_layout.addWidget(self.show_streamlines_cb)
        
        vis_group.setLayout(vis_layout)
        layout.addWidget(vis_group)
        
        # Contour settings
        contour_group = QGroupBox("Contour Settings")
        contour_layout = QVBoxLayout()
        
        contour_layout.addWidget(QLabel("Number of Levels:"))
        self.num_contours_spin = QSpinBox()
        self.num_contours_spin.setRange(5, 50)
        self.num_contours_spin.setValue(20)
        self.num_contours_spin.valueChanged.connect(self.update_visualization)
        contour_layout.addWidget(self.num_contours_spin)
        
        contour_group.setLayout(contour_layout)
        layout.addWidget(contour_group)
        
        # Vector settings
        vector_group = QGroupBox("Vector Settings")
        vector_layout = QVBoxLayout()
        
        vector_layout.addWidget(QLabel("Scale Factor:"))
        self.vector_scale_spin = QDoubleSpinBox()
        self.vector_scale_spin.setRange(0.01, 10.0)
        self.vector_scale_spin.setValue(1.0)
        self.vector_scale_spin.setSingleStep(0.1)
        self.vector_scale_spin.valueChanged.connect(self.update_visualization)
        vector_layout.addWidget(self.vector_scale_spin)
        
        vector_group.setLayout(vector_layout)
        layout.addWidget(vector_group)
        
        # Animation controls
        anim_group = QGroupBox("Animation")
        anim_layout = QVBoxLayout()
        
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_animation)
        self.play_button.setEnabled(False)
        anim_layout.addWidget(self.play_button)
        
        anim_layout.addWidget(QLabel("Time Step:"))
        self.timestep_slider = QSlider(Qt.Horizontal)
        self.timestep_slider.setMinimum(0)
        self.timestep_slider.setMaximum(100)
        self.timestep_slider.setValue(0)
        self.timestep_slider.setEnabled(False)
        anim_layout.addWidget(self.timestep_slider)
        
        anim_group.setLayout(anim_layout)
        layout.addWidget(anim_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return panel
        
    def create_viewer_widget(self) -> QWidget:
        """Create 3D viewer widget using PyVista"""
        if PYVISTA_AVAILABLE:
            # Create PyVista plotter with Qt backend
            self.plotter = QtInteractor(self)
            self.plotter.set_background('white')
            
            # Add axes
            self.plotter.add_axes()
            
            return self.plotter.interactor
        else:
            # Fallback to simple widget
            widget = QWidget()
            layout = QVBoxLayout(widget)
            label = QLabel("PyVista not available.\n3D visualization disabled.")
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont('Arial', 14))
            layout.addWidget(label)
            return widget
    
    def create_info_panel(self) -> QWidget:
        """Create right information panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Data info
        info_group = QGroupBox("Dataset Information")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Statistics
        stats_group = QGroupBox("Field Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        
        return panel
    
    def open_file(self):
        """Open CAFFA result file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open CAFFA Result File",
            "",
            "CAFFA Results (*.pos);;All Files (*)"
        )
        
        if filename:
            try:
                self.current_data = self.reader.read_binary_file(filename)
                self.update_data_info()
                self.create_mesh()
                self.update_visualization()
                self.statusBar().showMessage(f'Loaded: {filename}')
            except Exception as e:
                self.statusBar().showMessage(f'Error loading file: {str(e)}')
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        try:
            self.current_data = create_sample_data(50, 30)
            self.update_data_info()
            self.create_mesh()
            self.update_visualization()
            self.statusBar().showMessage('Sample data loaded')
        except Exception as e:
            self.statusBar().showMessage(f'Error creating sample data: {str(e)}')
    
    def create_mesh(self):
        """Create PyVista mesh from CAFFA data"""
        if not PYVISTA_AVAILABLE or self.current_data is None:
            return
        
        grid = self.current_data.grid
        
        # Create structured grid
        x = grid.xc.reshape(grid.nj, grid.ni)
        y = grid.yc.reshape(grid.nj, grid.ni)
        z = np.zeros_like(x)  # 2D data, z=0
        
        # Create PyVista StructuredGrid
        self.mesh = pv.StructuredGrid(x, y, z)
        
        # Add all fields to mesh
        self.mesh.point_data['U'] = self.current_data.u
        self.mesh.point_data['V'] = self.current_data.v
        self.mesh.point_data['Pressure'] = self.current_data.p
        self.mesh.point_data['Temperature'] = self.current_data.t
        self.mesh.point_data['TKE'] = self.current_data.te
        self.mesh.point_data['Dissipation'] = self.current_data.dissipation
        self.mesh.point_data['Velocity_Magnitude'] = self.current_data.velocity_magnitude
        
        # Create velocity vectors
        vectors = np.column_stack([
            self.current_data.u,
            self.current_data.v,
            np.zeros_like(self.current_data.u)
        ])
        self.mesh.point_data['Velocity'] = vectors
    
    def update_visualization(self):
        """Update the 3D visualization"""
        if not PYVISTA_AVAILABLE or self.mesh is None:
            return
        
        self.plotter.clear()
        
        # Map field name to data array
        field_map = {
            'Velocity Magnitude': 'Velocity_Magnitude',
            'U Velocity': 'U',
            'V Velocity': 'V',
            'Pressure': 'Pressure',
            'Temperature': 'Temperature',
            'Turbulent Kinetic Energy': 'TKE',
            'Dissipation': 'Dissipation'
        }
        
        current_field_name = self.field_combo.currentText()
        scalar_field = field_map.get(current_field_name, 'Velocity_Magnitude')
        
        # Show contours
        if self.show_contours_cb.isChecked():
            self.plotter.add_mesh(
                self.mesh,
                scalars=scalar_field,
                show_edges=self.show_mesh_cb.isChecked(),
                cmap='jet',
                n_colors=self.num_contours_spin.value(),
                scalar_bar_args={'title': current_field_name}
            )
        
        # Show vectors
        if self.show_vectors_cb.isChecked():
            scale = self.vector_scale_spin.value() * 0.1
            arrows = self.mesh.glyph(
                orient='Velocity',
                scale=scale,
                factor=scale
            )
            self.plotter.add_mesh(arrows, color='black', opacity=0.8)
        
        # Show streamlines
        if self.show_streamlines_cb.isChecked():
            # Create seed points
            seed_points = self.mesh.sample(100)
            streamlines = self.mesh.streamlines(
                vectors='Velocity',
                start_position=seed_points,
                max_time=100
            )
            self.plotter.add_mesh(
                streamlines,
                scalars=scalar_field,
                cmap='jet',
                line_width=2
            )
        
        # Add axes
        self.plotter.add_axes()
        
        # Update statistics
        self.update_statistics(scalar_field)
        
        self.plotter.render()
    
    def update_statistics(self, field_name: str):
        """Update field statistics display"""
        if self.mesh is None:
            return
        
        data = self.mesh.point_data[field_name]
        
        stats_text = f"""
<b>{field_name} Statistics:</b><br>
<br>
Minimum: {np.min(data):.6e}<br>
Maximum: {np.max(data):.6e}<br>
Mean: {np.mean(data):.6e}<br>
Std Dev: {np.std(data):.6e}<br>
<br>
Number of Points: {len(data)}<br>
        """
        
        self.stats_text.setHtml(stats_text)
    
    def update_data_info(self):
        """Update dataset information display"""
        if self.current_data is None:
            return
        
        grid = self.current_data.grid
        
        info_text = f"""
<b>Dataset Information:</b><br>
<br>
Time Step: {self.current_data.itim}<br>
Physical Time: {self.current_data.time:.6f}<br>
<br>
<b>Grid:</b><br>
NI: {grid.ni}<br>
NJ: {grid.nj}<br>
Total Cells: {grid.nij}<br>
<br>
X Range: [{np.min(grid.xc):.4f}, {np.max(grid.xc):.4f}]<br>
Y Range: [{np.min(grid.yc):.4f}, {np.max(grid.yc):.4f}]<br>
        """
        
        self.info_text.setHtml(info_text)
    
    def on_field_changed(self, field_name: str):
        """Handle field selection change"""
        self.update_visualization()
    
    def reset_camera(self):
        """Reset camera view"""
        if PYVISTA_AVAILABLE and hasattr(self, 'plotter'):
            self.plotter.reset_camera()
            self.plotter.render()
    
    def export_screenshot(self):
        """Export current view as screenshot"""
        if not PYVISTA_AVAILABLE or self.mesh is None:
            self.statusBar().showMessage('No data to export')
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        
        if filename:
            try:
                self.plotter.screenshot(filename)
                self.statusBar().showMessage(f'Screenshot saved: {filename}')
            except Exception as e:
                self.statusBar().showMessage(f'Error saving screenshot: {str(e)}')
    
    def toggle_animation(self):
        """Toggle animation playback"""
        # Placeholder for animation functionality
        self.statusBar().showMessage('Animation not yet implemented')
    
    def show_field_calculator(self):
        """Show field calculator dialog"""
        self.statusBar().showMessage('Field calculator not yet implemented')
    
    def show_about(self):
        """Show about dialog"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "About CAFFA Viewer",
            "CAFFA CFD Visualization Tool\n\n"
            "A Star CCM+ style interface for viewing CAFFA results.\n\n"
            "Built with PyQt5, PyVista, and VTK"
        )


def main():
    """Main entry point"""
    if not PYQT_AVAILABLE:
        print("Error: PyQt5 is required but not installed.")
        print("Install with: pip install PyQt5")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = CAFFAVisualizer()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
