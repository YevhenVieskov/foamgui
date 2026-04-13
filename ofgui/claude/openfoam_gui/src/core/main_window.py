"""
Main application window
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QMenuBar, QMenu, QToolBar, QStatusBar, QDockWidget,
    QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem, QAction
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import  QKeySequence
from pathlib import Path

from widgets.case_tree import CaseTreeWidget
from widgets.solver_config import SolverConfigWidget
from widgets.mesh_panel import MeshPanelWidget
from widgets.blockmesh_editor import BlockMeshEditorWidget
from widgets.residual_monitor import ResidualMonitorWidget
from widgets.contour_viewer import ContourViewerWidget
from core.case_manager import CaseManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    case_opened = pyqtSignal(str)
    case_closed = pyqtSignal()
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.case_manager = CaseManager(config)
        self.current_case = None
        
        self.setWindowTitle("OpenFOAM GUI - Star-CCM+ Style")
        self.setGeometry(100, 100, 1600, 900)
        
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_dock_widgets()
        self._create_central_widget()
        self._create_statusbar()
        
        # Connect signals
        self.case_opened.connect(self._on_case_opened)
        self.case_closed.connect(self._on_case_closed)
        
        # Setup auto-save timer
        if self.config.get('auto_save', True):
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self._auto_save)
            interval = self.config.get('auto_save_interval', 300) * 1000
            self.auto_save_timer.start(interval)
    
    def _create_actions(self):
        """Create application actions"""
        # File actions
        self.new_case_action = QAction("&New Case...", self)
        self.new_case_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_case_action.triggered.connect(self._new_case)
        
        self.open_case_action = QAction("&Open Case...", self)
        self.open_case_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_case_action.triggered.connect(self._open_case)
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self._save_case)
        self.save_action.setEnabled(False)
        
        self.close_case_action = QAction("&Close Case", self)
        self.close_case_action.setShortcut(QKeySequence.StandardKey.Close)
        self.close_case_action.triggered.connect(self._close_case)
        self.close_case_action.setEnabled(False)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.triggered.connect(self.close)
        
        # Mesh actions
        self.blockmesh_action = QAction("blockMesh Editor", self)
        self.blockmesh_action.triggered.connect(self._open_blockmesh_editor)
        self.blockmesh_action.setEnabled(False)
        
        self.snappy_action = QAction("snappyHexMesh Setup", self)
        self.snappy_action.triggered.connect(self._open_snappy_setup)
        self.snappy_action.setEnabled(False)
        
        self.cfmesh_action = QAction("cfMesh Setup", self)
        self.cfmesh_action.triggered.connect(self._open_cfmesh_setup)
        self.cfmesh_action.setEnabled(False)
        
        self.run_mesh_action = QAction("Run Mesher", self)
        self.run_mesh_action.triggered.connect(self._run_mesher)
        self.run_mesh_action.setEnabled(False)
        
        # Solver actions
        self.solver_config_action = QAction("Solver Configuration", self)
        self.solver_config_action.triggered.connect(self._open_solver_config)
        self.solver_config_action.setEnabled(False)
        
        self.run_solver_action = QAction("Run Solver", self)
        self.run_solver_action.triggered.connect(self._run_solver)
        self.run_solver_action.setEnabled(False)
        
        self.stop_solver_action = QAction("Stop Solver", self)
        self.stop_solver_action.triggered.connect(self._stop_solver)
        self.stop_solver_action.setEnabled(False)
        
        # View actions
        self.residuals_action = QAction("Show Residuals", self)
        self.residuals_action.setCheckable(True)
        self.residuals_action.setChecked(True)
        self.residuals_action.triggered.connect(self._toggle_residuals)
        
        self.contours_action = QAction("Show Contours", self)
        self.contours_action.setCheckable(True)
        self.contours_action.setChecked(True)
        self.contours_action.triggered.connect(self._toggle_contours)
    
    def _create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_case_action)
        file_menu.addAction(self.open_case_action)
        
        # Recent cases submenu
        self.recent_menu = file_menu.addMenu("Recent Cases")
        self._update_recent_menu()
        
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.close_case_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Mesh menu
        mesh_menu = menubar.addMenu("&Mesh")
        mesh_menu.addAction(self.blockmesh_action)
        mesh_menu.addAction(self.snappy_action)
        mesh_menu.addAction(self.cfmesh_action)
        mesh_menu.addSeparator()
        mesh_menu.addAction(self.run_mesh_action)
        
        # Solver menu
        solver_menu = menubar.addMenu("&Solver")
        solver_menu.addAction(self.solver_config_action)
        solver_menu.addSeparator()
        solver_menu.addAction(self.run_solver_action)
        solver_menu.addAction(self.stop_solver_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.residuals_action)
        view_menu.addAction(self.contours_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbars(self):
        """Create application toolbars"""
        # Main toolbar
        main_toolbar = QToolBar("Main Toolbar")
        main_toolbar.setMovable(False)
        self.addToolBar(main_toolbar)
        
        main_toolbar.addAction(self.new_case_action)
        main_toolbar.addAction(self.open_case_action)
        main_toolbar.addAction(self.save_action)
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.run_mesh_action)
        main_toolbar.addAction(self.run_solver_action)
        main_toolbar.addAction(self.stop_solver_action)
    
    def _create_dock_widgets(self):
        """Create dock widgets"""
        # Case tree dock
        self.case_tree_dock = QDockWidget("Case Tree", self)
        self.case_tree_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                            Qt.DockWidgetArea.RightDockWidgetArea)
        self.case_tree = CaseTreeWidget()
        self.case_tree_dock.setWidget(self.case_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.case_tree_dock)
    
    def _create_central_widget(self):
        """Create central widget with tabs"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Mesh tab
        self.mesh_panel = MeshPanelWidget(self.config)
        self.tab_widget.addTab(self.mesh_panel, "Mesh")
        
        # Solver configuration tab
        self.solver_config = SolverConfigWidget(self.config)
        self.tab_widget.addTab(self.solver_config, "Solver Setup")
        
        # Monitoring tab with splitter
        monitor_widget = QWidget()
        monitor_layout = QVBoxLayout(monitor_widget)
        monitor_layout.setContentsMargins(0, 0, 0, 0)
        
        monitor_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Residual monitor
        self.residual_monitor = ResidualMonitorWidget(self.config)
        monitor_splitter.addWidget(self.residual_monitor)
        
        # Contour viewer
        self.contour_viewer = ContourViewerWidget(self.config)
        monitor_splitter.addWidget(self.contour_viewer)
        
        monitor_splitter.setSizes([400, 400])
        monitor_layout.addWidget(monitor_splitter)
        
        self.tab_widget.addTab(monitor_widget, "Monitoring")
    
    def _create_statusbar(self):
        """Create status bar"""
        self.statusBar().showMessage("Ready")
    
    def _new_case(self):
        """Create new case"""
        from widgets.new_case_dialog import NewCaseDialog
        dialog = NewCaseDialog(self)
        if dialog.exec():
            case_data = dialog.get_case_data()
            case_path = self.case_manager.create_case(case_data)
            if case_path:
                self._load_case(case_path)
    
    def _open_case(self):
        """Open existing case"""
        case_path = QFileDialog.getExistingDirectory(
            self, "Open OpenFOAM Case", str(Path.home())
        )
        if case_path:
            self._load_case(case_path)
    
    def _save_case(self):
        """Save current case"""
        if self.current_case:
            self.case_manager.save_case(self.current_case)
            self.statusBar().showMessage(f"Case saved: {self.current_case}", 3000)
    
    def _auto_save(self):
        """Auto-save current case"""
        if self.current_case:
            self.case_manager.save_case(self.current_case)
    
    def _close_case(self):
        """Close current case"""
        if self.current_case:
            reply = QMessageBox.question(
                self, "Close Case",
                "Save changes before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self._save_case()
                self.current_case = None
                self.case_closed.emit()
            elif reply == QMessageBox.StandardButton.Discard:
                self.current_case = None
                self.case_closed.emit()
    
    def _load_case(self, case_path: str):
        """Load case"""
        try:
            self.case_manager.load_case(case_path)
            self.current_case = case_path
            self.config.add_recent_case(case_path)
            self._update_recent_menu()
            self.case_opened.emit(case_path)
            self.statusBar().showMessage(f"Case loaded: {case_path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load case: {e}")
    
    def _on_case_opened(self, case_path: str):
        """Handle case opened"""
        self.save_action.setEnabled(True)
        self.close_case_action.setEnabled(True)
        self.blockmesh_action.setEnabled(True)
        self.snappy_action.setEnabled(True)
        self.cfmesh_action.setEnabled(True)
        self.run_mesh_action.setEnabled(True)
        self.solver_config_action.setEnabled(True)
        self.run_solver_action.setEnabled(True)
        
        # Update widgets
        self.case_tree.load_case(case_path)
        self.mesh_panel.load_case(case_path)
        self.solver_config.load_case(case_path)
        
        self.setWindowTitle(f"OpenFOAM GUI - {Path(case_path).name}")
    
    def _on_case_closed(self):
        """Handle case closed"""
        self.save_action.setEnabled(False)
        self.close_case_action.setEnabled(False)
        self.blockmesh_action.setEnabled(False)
        self.snappy_action.setEnabled(False)
        self.cfmesh_action.setEnabled(False)
        self.run_mesh_action.setEnabled(False)
        self.solver_config_action.setEnabled(False)
        self.run_solver_action.setEnabled(False)
        self.stop_solver_action.setEnabled(False)
        
        self.setWindowTitle("OpenFOAM GUI")
    
    def _open_blockmesh_editor(self):
        """Open blockMesh visual editor"""
        if self.current_case:
            editor = BlockMeshEditorWidget(self.current_case, self.config)
            editor.show()
    
    def _open_snappy_setup(self):
        """Open snappyHexMesh setup"""
        # Will be implemented in mesh panel
        self.tab_widget.setCurrentWidget(self.mesh_panel)
        self.mesh_panel.show_snappy_setup()
    
    def _open_cfmesh_setup(self):
        """Open cfMesh setup"""
        self.tab_widget.setCurrentWidget(self.mesh_panel)
        self.mesh_panel.show_cfmesh_setup()
    
    def _run_mesher(self):
        """Run mesh generator"""
        if self.current_case:
            self.mesh_panel.run_mesher()
    
    def _open_solver_config(self):
        """Open solver configuration"""
        self.tab_widget.setCurrentWidget(self.solver_config)
    
    def _run_solver(self):
        """Run solver"""
        if self.current_case:
            self.case_manager.run_solver(self.current_case)
            self.run_solver_action.setEnabled(False)
            self.stop_solver_action.setEnabled(True)
            
            # Start monitoring
            self.residual_monitor.start_monitoring(self.current_case)
            self.contour_viewer.start_monitoring(self.current_case)
            
            self.tab_widget.setCurrentIndex(2)  # Switch to monitoring tab
    
    def _stop_solver(self):
        """Stop solver"""
        if self.current_case:
            self.case_manager.stop_solver()
            self.run_solver_action.setEnabled(True)
            self.stop_solver_action.setEnabled(False)
            
            # Stop monitoring
            self.residual_monitor.stop_monitoring()
            self.contour_viewer.stop_monitoring()
    
    def _toggle_residuals(self, checked: bool):
        """Toggle residuals display"""
        self.residual_monitor.setVisible(checked)
    
    def _toggle_contours(self, checked: bool):
        """Toggle contours display"""
        self.contour_viewer.setVisible(checked)
    
    def _update_recent_menu(self):
        """Update recent cases menu"""
        self.recent_menu.clear()
        recent_cases = self.config.get('recent_cases', [])
        
        for case_path in recent_cases:
            action = QAction(case_path, self)
            action.triggered.connect(lambda checked, p=case_path: self._load_case(p))
            self.recent_menu.addAction(action)
        
        if not recent_cases:
            action = QAction("No recent cases", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
    
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About OpenFOAM GUI",
            "OpenFOAM GUI v1.0.0\n\n"
            "A Star-CCM+ style interface for OpenFOAM 2506\n\n"
            "Features:\n"
            "• Visual blockMesh editor\n"
            "• Solver configuration generator\n"
            "• Mesh generation (blockMesh, snappyHexMesh, cfMesh)\n"
            "• Real-time monitoring\n"
            "• Residual plots and contour visualization"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.current_case:
            self._close_case()
            if self.current_case:  # User cancelled
                event.ignore()
                return
        event.accept()
