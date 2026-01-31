import sys
import subprocess
import threading
import time
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDockWidget, QTreeWidget, 
                             QTreeWidgetItem, QVBoxLayout, QWidget, QGroupBox, 
                             QFormLayout, QDoubleSpinBox, QSpinBox, QComboBox, 
                             QPushButton, QLabel, QSplitter, QFileDialog, QCheckBox, 
                             QMessageBox, QToolBar, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from pyvistaqt import QtInteractor
import pyvista as pv

# Embedding Matplotlib for Residuals
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from caffa_io import CaffaIO

# --- Worker for Live Fortran Execution ---
class SolverWorker(QObject):
    update_residuals = pyqtSignal(dict)
    finished = pyqtSignal()
    log_message = pyqtSignal(str)

    def run_solver(self, executable):
        try:
            # Start the Fortran process
            process = subprocess.Popen(
                [executable], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1
            )
            
            # Real-time output parsing
            for line in process.stdout:
                self.log_message.emit(line.strip())
                if "RESIDUAL" in line or "ITER" in line:
                    self._parse_residual(line)
            
            process.wait()
            self.finished.emit()
            
        except FileNotFoundError:
            self.log_message.emit("Error: Executable not found. Running Mock Mode.")
            self._mock_simulation()

    def _parse_residual(self, line):
        # Heuristic parsing of CAFFA standard output
        # Example: GRID 1 CYCLE 10 ITER 5 ... RESIDUALS ...
        try:
            parts = line.split()
            # Assuming columns: ITER is index 2, Res1 index 3...
            # This logic adapts to the exact format in caffa.f PRINT statement
            if len(parts) > 5 and parts[0].isdigit(): 
                iteration = int(parts[1])
                res_u = float(parts[3])
                res_v = float(parts[4])
                res_p = float(parts[5])
                self.update_residuals.emit({
                    'iter': iteration, 
                    'U': res_u, 
                    'V': res_v, 
                    'P': res_p
                })
        except ValueError:
            pass

    def _mock_simulation(self):
        """Generates fake residuals for testing GUI without Fortran exe."""
        for i in range(1, 101):
            time.sleep(0.05)
            res = {
                'iter': i, 
                'U': 10**(-i/20.0), 
                'V': 10**(-i/22.0), 
                'P': 10**(-i/15.0)
            }
            self.update_residuals.emit(res)
            self.log_message.emit(f"GRID 1 CYCLE {i} RES: {res['U']:.2e} {res['V']:.2e}")
        self.finished.emit()


# --- Custom Matplotlib Widget for Residuals ---
class ResidualPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_yscale('log')
        self.ax.set_title("Residuals")
        self.ax.grid(True)
        
        self.data = {'iter': [], 'U': [], 'V': [], 'P': []}
        self.lines = {}

    def update_plot(self, res_data):
        self.data['iter'].append(res_data['iter'])
        self.data['U'].append(res_data['U'])
        self.data['V'].append(res_data['V'])
        self.data['P'].append(res_data['P'])
        
        self.ax.clear()
        self.ax.set_yscale('log')
        self.ax.grid(True)
        self.ax.plot(self.data['iter'], self.data['U'], label='U-Mom')
        self.ax.plot(self.data['iter'], self.data['V'], label='V-Mom')
        self.ax.plot(self.data['iter'], self.data['P'], label='Pressure')
        self.ax.legend(loc='upper right')
        self.canvas.draw()

    def clear(self):
        self.data = {'iter': [], 'U': [], 'V': [], 'P': []}
        self.ax.clear()
        self.canvas.draw()


# --- Main Application Window ---
class CaffaStarGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCAFFA Studio (STAR-CCM+ Style)")
        self.resize(1400, 900)
        self.io = CaffaIO()
        self.worker_thread = None

        # --- Main Splitter (Left: Tree, Center: Scene, Bottom: Output) ---
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)

        # 1. Left Panel (Simulation Tree & Properties)
        left_panel = QSplitter(Qt.Orientation.Vertical)
        
        # Simulation Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Simulation Tree")
        self.tree.itemClicked.connect(self.on_tree_click)
        left_panel.addWidget(self.tree)
        
        # Property Editor (Docked below tree)
        self.props_group = QGroupBox("Properties")
        self.props_layout = QFormLayout()
        self.props_group.setLayout(self.props_layout)
        prop_container = QWidget()
        prop_box = QVBoxLayout()
        prop_box.addWidget(self.props_group)
        prop_box.addStretch()
        prop_container.setLayout(prop_box)
        left_panel.addWidget(prop_container)
        
        main_splitter.addWidget(left_panel)

        # 2. Center Panel (3D View)
        self.plotter = QtInteractor(self)
        self.plotter.set_background("white") 
        self.plotter.add_axes()
        main_splitter.addWidget(self.plotter.interactor)

        # 3. Right Panel (Residuals & Actions)
        right_panel = QSplitter(Qt.Orientation.Vertical)
        
        self.residuals_widget = ResidualPlotWidget()
        right_panel.addWidget(self.residuals_widget)
        
        # Output Log
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(1)
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setHeaderLabels(["Solver Output"])
        right_panel.addWidget(self.log_table)
        
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 800, 300])

        # --- Initialize Data ---
        self.build_tree()
        self.load_default_mesh()

        # --- Toolbar ---
        toolbar = self.addToolBar("Main")
        toolbar.addAction("Import Grid").triggered.connect(self.import_grid)
        toolbar.addAction("Run Solver").triggered.connect(self.run_solver_thread)

    def build_tree(self):
        """Builds the STAR-CCM+ like simulation tree."""
        self.tree.clear()
        
        # Root Node
        self.root = QTreeWidgetItem(self.tree, ["Simulation_1"])
        
        # Readme / Metadata Node
        self.meta_node = QTreeWidgetItem(self.root, ["Model Description"])
        
        # Geometry / Mesh
        self.mesh_node = QTreeWidgetItem(self.root, ["Mesh"])
        self.regions_node = QTreeWidgetItem(self.mesh_node, ["Regions"])
        
        # Physics
        self.physics_node = QTreeWidgetItem(self.root, ["Physics"])
        QTreeWidgetItem(self.physics_node, ["Models"])
        QTreeWidgetItem(self.physics_node, ["Initial Conditions"])
        
        # Boundaries
        self.bc_node = QTreeWidgetItem(self.root, ["Boundaries"])
        # Example BCs (would be populated from grid file in reality)
        QTreeWidgetItem(self.bc_node, ["Inlet"])
        QTreeWidgetItem(self.bc_node, ["Outlet"])
        QTreeWidgetItem(self.bc_node, ["Wall"])

        self.root.setExpanded(True)
        self.mesh_node.setExpanded(True)

    def on_tree_click(self, item, col):
        """Update Property Panel based on selection."""
        # Clear props
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        text = item.text(0)
        self.props_group.setTitle(f"Properties: {text}")
        
        if text == "Model Description":
            self.show_readme_props()
        elif text in ["Inlet", "Outlet", "Wall"]:
            self.show_bc_editor(text)
        elif text == "Initial Conditions":
            self.show_initial_props()

    def show_readme_props(self):
        """Auto-populate metadata from README."""
        meta = self.io.parse_readme("Readme") # Checks local file
        
        self.props_layout.addRow("Title:", QLabel(meta.get("title", "-")))
        self.props_layout.addRow("Version:", QLabel(meta.get("version", "-")))
        self.props_layout.addRow("Author:", QLabel(meta.get("author", "-")))
        
        if meta["models"]:
            lbl = QLabel(", ".join(meta["models"]))
            lbl.setWordWrap(True)
            self.props_layout.addRow("Features:", lbl)

    def show_bc_editor(self, bc_name):
        """Boundary Condition Editor."""
        cb_type = QComboBox()
        cb_type.addItems(["Velocity Inlet", "Pressure Outlet", "Wall (No-Slip)", "Symmetry"])
        self.props_layout.addRow("Type:", cb_type)
        
        if bc_name == "Inlet":
            sb_u = QDoubleSpinBox()
            sb_u.setValue(1.0)
            self.props_layout.addRow("Velocity X (m/s):", sb_u)
            self.props_layout.addRow(QLabel("")) # Citation context

    def show_initial_props(self):
        """Editors for UIN, VIN, PIN etc."""
        self.props_layout.addRow("U Init:", QDoubleSpinBox())
        self.props_layout.addRow("V Init:", QDoubleSpinBox())
        self.props_layout.addRow("P Init:", QDoubleSpinBox())

    def load_default_mesh(self):
        """Loads grid and displays it."""
        # Try finding a real grid, else dummy
        grid = self.io.import_real_mesh("test.grd")
        self.update_scene(grid)

    def import_grid(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open Grid", "", "CAFFA Grid (*.grd)")
        if fname:
            grid = self.io.import_real_mesh(fname)
            self.update_scene(grid)

    def update_scene(self, grid):
        self.plotter.clear()
        self.plotter.add_mesh(grid, show_edges=True, color="lightblue", opacity=0.5)
        self.plotter.add_axes()
        self.plotter.reset_camera()

    def run_solver_thread(self):
        """Starts the Fortran execution with live monitoring."""
        self.residuals_widget.clear()
        self.log_table.setRowCount(0)
        
        self.worker = SolverWorker()
        self.thread = threading.Thread(target=self.worker.run_solver, args=("caffa.exe",))
        
        # Connect Signals
        self.worker.update_residuals.connect(self.residuals_widget.update_plot)
        self.worker.log_message.connect(self.append_log)
        self.worker.finished.connect(lambda: self.statusBar().showMessage("Solver Finished"))
        
        self.thread.start()
        self.statusBar().showMessage("Solver Running...")

    def append_log(self, text):
        row = self.log_table.rowCount()
        self.log_table.insertRow(row)
        self.log_table.setItem(row, 0, QTableWidgetItem(text))
        self.log_table.scrollToBottom()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CaffaStarGUI()
    window.show()
    sys.exit(app.exec())