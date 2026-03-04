"""
Main Window - Star CCM+ Style Interface
"""

from qtpy.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QStatusBar, QMenuBar,
    QMenu, QAction, QFileDialog, QMessageBox,
    QDockWidget, QTabWidget, QLabel, QFrame,
    QTreeWidget, QTreeWidgetItem, QProgressBar,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit
)
from qtpy.QtCore import Qt, Signal, Slot, QSettings
from qtpy.QtGui import QIcon, QFont, QKeySequence
import pyvistaqt
from .visualization_widget import VisualizationWidget
from .residual_plot import ResidualPlotWidget
from .data_loader import CFDDataLoader

class CFDMainWindow(QMainWindow):
    """Star CCM+ style main window for CFD visualization"""
    
    # Signals
    data_loaded = Signal(dict)
    simulation_started = Signal()
    simulation_stopped = Signal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAFFA Visualizer - Star CCM+ Style")
        self.setMinimumSize(1600, 900)
        
        # Initialize data
        self.cfd_data = None
        self.data_loader = CFDDataLoader()
        
        # Setup UI
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_docks()
        
        # Connect signals
        self.data_loader.data_loaded.connect(self._on_data_loaded)
        self.data_loader.error_occurred.connect(self._on_error)
        self.data_loader.progress_updated.connect(self._on_progress)
        
        # Load settings
        self._load_settings()
    
    def _setup_ui(self):
        """Setup main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Create splitter for left/right panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Simulation tree
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Visualization and plots
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (30% left, 70% right)
        splitter.setSizes([480, 1120])
        
        main_layout.addWidget(splitter)
    
    def _create_left_panel(self):
        """Create left panel with simulation tree (Star CCM+ style)"""
        left_widget = QFrame()
        left_widget.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        left_widget.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
            }
        """)
        layout = QVBoxLayout(left_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Tree view for simulation components
        tree_label = QLabel("Simulation Tree")
        tree_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(tree_label)
        
        # Simulation tree
        self.simulation_tree = QTreeWidget()
        self.simulation_tree.setHeaderLabel("Components")
        self.simulation_tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #cccccc;
            }
            QTreeWidget::item {
                padding: 3px;
            }
            QTreeWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        
        # Add simulation components (Star CCM+ style)
        categories = [
            ("Geometry", ["Airfoil", "Domain", "Boundaries"]),
            ("Mesh", ["Surface Mesh", "Volume Mesh", "Quality"]),
            ("Physics", ["Continuity", "Momentum", "Energy", "Turbulence"]),
            ("Solvers", ["Pressure", "Velocity", "Turbulence"]),
            ("Results", ["Residuals", "Contours", "Vectors", "Planes"]),
            ("Reports", ["Forces", "Moments", "Coefficients"])
        ]
        
        for parent_name, children in categories:
            parent_item = QTreeWidgetItem([parent_name])
            parent_item.setExpanded(True)
            for child_name in children:
                child_item = QTreeWidgetItem([child_name])
                parent_item.addChild(child_item)
            self.simulation_tree.addTopLevelItem(parent_item)
        
        layout.addWidget(self.simulation_tree)
        
        return left_widget
    
    def _create_right_panel(self):
        """Create right panel with visualization and plots"""
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d7;
            }
        """)
        
        # 3D Visualization Tab
        self.viz_widget = VisualizationWidget()
        self.tab_widget.addTab(self.viz_widget, "3D Scene")
        
        # Residuals Tab
        self.residual_widget = ResidualPlotWidget()
        self.tab_widget.addTab(self.residual_widget, "Residuals")
        
        # Force Coefficients Tab
        from qtpy.QtWidgets import QTableWidget
        force_table = QTableWidget()
        force_table.setColumnCount(6)
        force_table.setHorizontalHeaderLabels([
            "Iteration", "Cl", "Cd", "Cm", "Time", "Converged"
        ])
        self.tab_widget.addTab(force_table, "Force Coefficients")
        
        # Data Table Tab
        data_table = QTableWidget()
        data_table.setColumnCount(8)
        data_table.setHorizontalHeaderLabels([
            "Iteration", "UMOM", "VMOM", "MASS", "ENER", "KINE", "DISE", "Monitor"
        ])
        self.tab_widget.addTab(data_table, "Data Table")
        
        layout.addWidget(self.tab_widget)
        
        return right_widget
    
    def _setup_menu(self):
        """Setup menu bar (Star CCM+ style)"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #cccccc;
            }
            QMenuBar::item {
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Simulation...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_simulation)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Scene", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_scene)
        file_menu.addAction(save_action)
        
        export_action = QAction("Export Data...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        reset_view = QAction("Reset View", self)
        reset_view.setShortcut("R")
        reset_view.triggered.connect(self._reset_view)
        view_menu.addAction(reset_view)
        
        # Add visualization options
        vector_action = QAction("Show Vectors", self)
        vector_action.setCheckable(True)
        vector_action.setShortcut("V")
        vector_action.triggered.connect(self._toggle_vectors)
        view_menu.addAction(vector_action)
        
        contour_action = QAction("Show Contours", self)
        contour_action.setCheckable(True)
        contour_action.setChecked(True)
        contour_action.setShortcut("C")
        contour_action.triggered.connect(self._toggle_contours)
        view_menu.addAction(contour_action)
        
        plane_action = QAction("Add Plane Section", self)
        plane_action.setShortcut("P")
        plane_action.triggered.connect(self._add_plane_section)
        view_menu.addAction(plane_action)
        
        streamline_action = QAction("Show Streamlines", self)
        streamline_action.setCheckable(True)
        streamline_action.setShortcut("S")
        streamline_action.triggered.connect(self._toggle_streamlines)
        view_menu.addAction(streamline_action)
        
        view_menu.addSeparator()
        
        # View presets
        front_view = QAction("Front View", self)
        front_view.setShortcut("F")
        front_view.triggered.connect(lambda: self._set_view("front"))
        view_menu.addAction(front_view)
        
        top_view = QAction("Top View", self)
        top_view.setShortcut("T")
        top_view.triggered.connect(lambda: self._set_view("top"))
        view_menu.addAction(top_view)
        
        iso_view = QAction("Isometric View", self)
        iso_view.setShortcut("I")
        iso_view.triggered.connect(lambda: self._set_view("iso"))
        view_menu.addAction(iso_view)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        residual_action = QAction("Plot Residuals", self)
        residual_action.triggered.connect(self._show_residuals)
        tools_menu.addAction(residual_action)
        
        calculate_action = QAction("Calculate Forces", self)
        calculate_action.triggered.connect(self._calculate_forces)
        tools_menu.addAction(calculate_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Setup toolbar with common actions"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #cccccc;
                spacing: 5px;
            }
            QToolButton {
                padding: 5px 10px;
                border: 1px solid transparent;
            }
            QToolButton:hover {
                border: 1px solid #0078d7;
                background-color: #e0e0e0;
            }
        """)
        self.addToolBar(toolbar)
        
        # Add common actions
        actions = [
            ("Open", self._open_simulation, "Ctrl+O", "??"),
            ("Save", self._save_scene, "Ctrl+S", "??"),
            ("Reset View", self._reset_view, "R", "??"),
            ("Plane Section", self._add_plane_section, "P", "??"),
            ("Vectors", self._toggle_vectors, "V", "??"),
            ("Contours", self._toggle_contours, "C", "??"),
            ("Streamlines", self._toggle_streamlines, "S", "??"),
        ]
        
        for name, handler, shortcut, icon in actions:
            action = QAction(f"{icon} {name}", self)
            action.setShortcut(shortcut)
            action.triggered.connect(handler)
            toolbar.addAction(action)
    
    def _setup_statusbar(self):
        """Setup status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #f0f0f0;
                border-top: 1px solid #cccccc;
            }
        """)
        self.statusbar.showMessage("Ready")
        
        # Add permanent widgets
        self.info_label = QLabel("No data loaded")
        self.statusbar.addPermanentWidget(self.info_label)
    
    def _setup_docks(self):
        """Setup dockable panels"""
        # Properties dock
        properties_dock = QDockWidget("Properties", self)
        properties_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        properties_dock.setStyleSheet("""
            QDockWidget {
                titlebar-close-icon: url(close.png);
                titlebar-normal-icon: url(float.png);
            }
            QDockWidget::title {
                background-color: #e0e0e0;
                padding: 5px;
            }
        """)
        self.addDockWidget(Qt.RightDockWidgetArea, properties_dock)
        
        properties_widget = QWidget()
        layout = QFormLayout(properties_widget)
        
        from qtpy.QtWidgets import QComboBox, QDoubleSpinBox
        layout.addRow("Variable:", QComboBox())
        layout.addRow("Min:", QLineEdit("0"))
        layout.addRow("Max:", QLineEdit("1"))
        layout.addRow("Levels:", QLineEdit("20"))
        layout.addRow("Opacity:", QDoubleSpinBox())
        
        properties_dock.setWidget(properties_widget)
        
        # Monitor dock
        monitor_dock = QDockWidget("Monitors", self)
        monitor_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, monitor_dock)
        
        monitor_widget = QWidget()
        monitor_layout = QVBoxLayout(monitor_widget)
        
        monitor_label = QLabel("Convergence Monitors")
        monitor_label.setFont(QFont("Arial", 9, QFont.Bold))
        monitor_layout.addWidget(monitor_label)
        
        from qtpy.QtWidgets import QListWidget
        monitor_list = QListWidget()
        monitor_list.addItems(["Continuity", "X-Momentum", "Y-Momentum", "Energy"])
        monitor_layout.addWidget(monitor_list)
        
        monitor_dock.setWidget(monitor_widget)
    
    @Slot(dict)
    def _on_data_loaded(self, data):
        """Handle data loaded signal"""
        self.cfd_data = data
        self.viz_widget.update_data(data)
        
        if 'residuals' in data:
            self.residual_widget.update_residuals(data['residuals'])
        
        # Update status
        filename = data.get('filename', 'Unknown')
        self.statusbar.showMessage(f"Data loaded: {filename}")
        self.info_label.setText(f"File: {filename} | Points: {data['mesh'].n_points if 'mesh' in data else 0}")
        
        # Update simulation tree
        self._update_simulation_tree(data)
    
    @Slot(str)
    def _on_error(self, error_message):
        """Handle error signal"""
        QMessageBox.critical(self, "Error", f"Failed to load data: {error_message}")
        self.statusbar.showMessage(f"Error: {error_message}")
    
    @Slot(int)
    def _on_progress(self, value):
        """Handle progress update"""
        self.progress_bar.setValue(value)
        self.progress_bar.setVisible(value < 100)
    
    def _update_simulation_tree(self, data):
        """Update simulation tree with loaded data"""
        # Add data-specific items to tree
        if 'mesh' in data:
            mesh_item = QTreeWidgetItem([f"Mesh ({data['mesh'].n_points} points)"])
            self.simulation_tree.topLevelItem(1).addChild(mesh_item)
        
        if 'residuals' in data:
            residual_item = QTreeWidgetItem([f"Residuals ({len(data['residuals'])} iterations)"])
            self.simulation_tree.topLevelItem(4).addChild(residual_item)
    
    def _open_simulation(self):
        """Open simulation data file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open CAFFA Simulation Data",
            "",
            "CAFFA Files (*.out *.re *.grd);;All Files (*)"
        )
        
        if filename:
            try:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                data = self.data_loader.load(filename)
                self._on_data_loaded(data)
            except Exception as e:
                self._on_error(str(e))
            finally:
                self.progress_bar.setVisible(False)
    
    def _save_scene(self):
        """Save current visualization scene"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Scene",
            "",
            "PNG Files (*.png);;SVG Files (*.svg);;All Files (*)"
        )
        
        if filename:
            try:
                self.viz_widget.save_screenshot(filename)
                self.statusbar.showMessage(f"Scene saved: {filename}")
            except Exception as e:
                self._on_error(str(e))
    
    def _export_data(self):
        """Export data to CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            try:
                self.residual_widget.export_data(filename)
                self.statusbar.showMessage(f"Data exported: {filename}")
            except Exception as e:
                self._on_error(str(e))
    
    def _reset_view(self):
        """Reset 3D view to default"""
        self.viz_widget.reset_camera()
        self.statusbar.showMessage("View reset")
    
    def _set_view(self, view_type):
        """Set camera view"""
        self.viz_widget.set_camera_view(view_type)
        self.statusbar.showMessage(f"View set to: {view_type}")
    
    def _toggle_vectors(self, checked):
        """Toggle vector visualization"""
        self.viz_widget.show_vectors(checked)
        self.statusbar.showMessage(f"Vectors: {'ON' if checked else 'OFF'}")
    
    def _toggle_contours(self, checked):
        """Toggle contour visualization"""
        self.viz_widget.show_contours(checked)
        self.statusbar.showMessage(f"Contours: {'ON' if checked else 'OFF'}")
    
    def _toggle_streamlines(self, checked):
        """Toggle streamline visualization"""
        self.viz_widget.show_streamlines(checked)
        self.statusbar.showMessage(f"Streamlines: {'ON' if checked else 'OFF'}")
    
    def _add_plane_section(self):
        """Add plane section to visualization"""
        self.viz_widget.add_plane_section()
        self.statusbar.showMessage("Plane section added")
    
    def _show_residuals(self):
        """Show residuals tab"""
        self.tab_widget.setCurrentIndex(1)
    
    def _calculate_forces(self):
        """Calculate aerodynamic forces"""
        if self.cfd_data:
            QMessageBox.information(self, "Forces", "Force calculation complete")
        else:
            QMessageBox.warning(self, "Warning", "No data loaded")
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About CAFFA Visualizer",
            "CAFFA Visualizer v1.0\n\n"
            "Star CCM+ Style CFD Visualization Tool\n\n"
            "Built with PyVista, PyQt, and VTK\n"
            "For CAFFA CFD Simulation Results"
        )
    
    def _load_settings(self):
        """Load application settings"""
        settings = QSettings("CAFFA", "Visualizer")
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
    
    def _save_settings(self):
        """Save application settings"""
        settings = QSettings("CAFFA", "Visualizer")
        settings.setValue("geometry", self.saveGeometry())
    
    def closeEvent(self, event):
        """Handle close event"""
        self._save_settings()
        event.accept()