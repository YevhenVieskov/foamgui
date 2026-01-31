import sys
import subprocess
import threading
import time
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, 
                             QVBoxLayout, QWidget, QGroupBox, QFormLayout, 
                             QDoubleSpinBox, QComboBox, QLabel, QSplitter, 
                             QFileDialog, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from pyvistaqt import QtInteractor
import pyvista as pv

# Embedding Matplotlib for Residuals
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Import IO logic (Assumes caffa_io.py exists from previous step)
from caffa_io import CaffaIO

# --- Worker for Live Fortran Execution & Field Data ---
class SolverWorker(QObject):
    update_residuals = pyqtSignal(dict)
    update_fields = pyqtSignal(dict)  # Signal for 3D field data
    finished = pyqtSignal()
    log_message = pyqtSignal(str)

    def run_solver(self, executable):
        try:
            # Attempt to run real executable
            process = subprocess.Popen(
                [executable], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1
            )
            
            for line in process.stdout:
                self.log_message.emit(line.strip())
                if "RESIDUAL" in line or "ITER" in line:
                    self._parse_residual(line)
            
            process.wait()
            self.finished.emit()
            
        except FileNotFoundError:
            self.log_message.emit("Executable not found. Starting Mock Solver with Field Visualization...")
            self._mock_simulation()

    def _parse_residual(self, line):
        # ... (Same residual parsing logic as before) ...
        try:
            parts = line.split()
            if len(parts) > 5 and parts[0].isdigit(): 
                res = {
                    'iter': int(parts[1]), 
                    'U': float(parts[3]), 
                    'V': float(parts[4]), 
                    'P': float(parts[5])
                }
                self.update_residuals.emit(res)
        except ValueError:
            pass

    def _mock_simulation(self):
        """
        Generates residuals AND changing field data (P, U, V) 
        to demonstrate real-time plotting capabilities.
        """
        # Grid dimensions must match the dummy grid in CaffaIO (50x30 = 1500 pts)
        ni, nj = 50, 30
        x = np.linspace(0, 5, ni)
        y = np.linspace(0, 2, nj)
        xx, yy = np.meshgrid(x, y, indexing='ij')
        
        for t in range(1, 101):
            time.sleep(0.1) # Simulating compute time
            
            # 1. Emit Residuals
            res = {
                'iter': t, 
                'U': 10**(-t/20.0) + np.random.rand()*1e-4, 
                'V': 10**(-t/22.0) + np.random.rand()*1e-4, 
                'P': 10**(-t/15.0) + np.random.rand()*1e-4
            }
            self.update_residuals.emit(res)
            self.log_message.emit(f"ITER {t} | RES U: {res['U']:.1e} | UPDATING FIELDS...")

            # 2. Emit Field Data (Dynamic Waves)
            # Pressure Pulse
            p_field = np.sin(xx - t*0.1) * np.cos(yy)
            
            # Velocity Vector (Vortex-ish)
            u_field = -np.sin(yy) * np.cos(xx - t*0.1)
            v_field = np.cos(yy) * np.sin(xx - t*0.1)
            
            # Pack into dictionary
            field_data = {
                'iter': t,
                'Pressure': p_field.flatten(order='F'),
                'Velocity_X': u_field.flatten(order='F'),
                'Velocity_Y': v_field.flatten(order='F')
            }
            self.update_fields.emit(field_data)

        self.finished.emit()


# --- Custom Matplotlib Widget for Residuals ---
class ResidualPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.figure.patch.set_facecolor('#f0f0f0') # Light gray background
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_yscale('log')
        self.ax.set_title("Residuals Monitor")
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        self.data = {'iter': [], 'U': [], 'V': [], 'P': []}

    def update_plot(self, res_data):
        self.data['iter'].append(res_data['iter'])
        self.data['U'].append(res_data['U'])
        self.data['V'].append(res_data['V'])
        self.data['P'].append(res_data['P'])
        
        self.ax.clear()
        self.ax.set_yscale('log')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.plot(self.data['iter'], self.data['U'], label='U-Mom', color='blue')
        self.ax.plot(self.data['iter'], self.data['V'], label='V-Mom', color='green')
        self.ax.plot(self.data['iter'], self.data['P'], label='Pressure', color='red')
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
        self.resize(1600, 900)
        self.io = CaffaIO()
        self.worker_thread = None
        self.active_grid = None # Store the VTK grid object

        # --- Main Splitter ---
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_splitter)

        # 1. Left Panel (Tree & Properties)
        left_panel = QSplitter(Qt.Orientation.Vertical)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Simulation Tree")
        self.tree.itemClicked.connect(self.on_tree_click)
        left_panel.addWidget(self.tree)
        
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

        # 2. Center Panel: Tabbed Scenes (Mesh, Pressure, Velocity)
        self.scene_tabs = QTabWidget()
        self.scene_tabs.setTabPosition(QTabWidget.TabPosition.South)
        
        # Initialize Plotters
        self.plotters = {}
        self._init_scene_tab("Geometry Scene", "Mesh")
        self._init_scene_tab("Scalar Scene 1", "Pressure")
        self._init_scene_tab("Vector Scene 1", "Velocity")
        
        main_splitter.addWidget(self.scene_tabs)

        # 3. Right Panel (Residuals & Log)
        right_panel = QSplitter(Qt.Orientation.Vertical)
        self.residuals_widget = ResidualPlotWidget()
        right_panel.addWidget(self.residuals_widget)
        
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(1)
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setHeaderLabels(["Output Log"])
        right_panel.addWidget(self.log_table)
        
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([250, 1000, 350])

        # --- Data & Toolbar ---
        self.build_tree()
        self.load_default_mesh() # Creates self.active_grid

        toolbar = self.addToolBar("Main")
        toolbar.addAction("Import Grid").triggered.connect(self.import_grid)
        toolbar.addAction("Run Solver").triggered.connect(self.run_solver_thread)

    def _init_scene_tab(self, name, key):
        """Helper to create PyVista tabs."""
        plotter = QtInteractor(self.scene_tabs)
        plotter.set_background("white")
        plotter.add_axes()
        self.scene_tabs.addTab(plotter.interactor, name)
        self.plotters[key] = plotter

    def build_tree(self):
        self.tree.clear()
        self.root = QTreeWidgetItem(self.tree, ["Simulation_1"])
        QTreeWidgetItem(self.root, ["Physics"])
        mesh_node = QTreeWidgetItem(self.root, ["Mesh"])
        self.root.setExpanded(True)
        mesh_node.setExpanded(True)

    def on_tree_click(self, item, col):
        # Basic Property clearing logic
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        self.props_group.setTitle(f"Properties: {item.text(0)}")

    def load_default_mesh(self):
        self.active_grid = self.io.import_real_mesh("test.grd")
        self.reset_all_scenes()

    def import_grid(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open Grid", "", "CAFFA Grid (*.grd)")
        if fname:
            self.active_grid = self.io.import_real_mesh(fname)
            self.reset_all_scenes()

    def reset_all_scenes(self):
        """Initializes all plotters with the base mesh."""
        if not self.active_grid: return

        # 1. Geometry Scene (Mesh Only)
        p_mesh = self.plotters['Mesh']
        p_mesh.clear()
        p_mesh.add_mesh(self.active_grid, show_edges=True, color="lightblue", opacity=0.3)
        p_mesh.view_xy()
        p_mesh.reset_camera()

        # 2. Scalar Scene (Pressure) - Initialize with blank/zero
        p_pres = self.plotters['Pressure']
        p_pres.clear()
        p_pres.add_mesh(self.active_grid, scalars=None, show_edges=False, cmap="jet")
        p_pres.view_xy()
        p_pres.reset_camera()

        # 3. Vector Scene (Velocity)
        p_vel = self.plotters['Velocity']
        p_vel.clear()
        # Add base mesh for context
        p_vel.add_mesh(self.active_grid, color="white", opacity=0.2, show_edges=True)
        p_vel.view_xy()
        p_vel.reset_camera()

    def run_solver_thread(self):
        self.residuals_widget.clear()
        self.log_table.setRowCount(0)
        
        self.worker = SolverWorker()
        self.thread = threading.Thread(target=self.worker.run_solver, args=("caffa.exe",))
        
        # Connect Signals
        self.worker.update_residuals.connect(self.residuals_widget.update_plot)
        self.worker.update_fields.connect(self.update_live_scenes) # New Signal
        self.worker.log_message.connect(self.append_log)
        
        self.thread.start()
        self.statusBar().showMessage("Solver Running - Realtime Vis Active")

    def update_live_scenes(self, data):
        """
        Slot called by Worker to update 3D scenes in real-time.
        data: dict containing 'Pressure', 'Velocity_X', 'Velocity_Y' arrays.
        """
        if not self.active_grid: return

        # 1. Update Underlying Grid Data
        # PyVista/VTK arrays can be updated in place efficiently
        try:
            self.active_grid.point_data["Pressure"] = data['Pressure']
            
            # Combine Components for Velocity Vector
            u = data['Velocity_X']
            v = data['Velocity_Y']
            w = np.zeros_like(u)
            vectors = np.column_stack((u, v, w))
            self.active_grid.point_data["Velocity"] = vectors
        except ValueError as e:
            # Handle mismatch if grid size changed
            self.append_log(f"Vis Error: Grid size mismatch. {e}")
            return

        # 2. Update Pressure Scene (Scalar)
        # We assume the mesh actor is already added. We force a redraw/scalar update.
        # Note: In PyVistaQt, we usually clear/add for total refresh or use actor.mapper 
        # For simplicity in this demo, we re-add the mesh which is fast enough for ~1500 cells.
        
        p_pres = self.plotters['Pressure']
        p_pres.clear()
        p_pres.add_mesh(self.active_grid, scalars="Pressure", cmap="jet", show_edges=False, show_scalar_bar=True)
        # Prevent camera reset on every update to maintain zoom
        
        # 3. Update Velocity Scene (Vectors)
        p_vel = self.plotters['Velocity']
        p_vel.clear()
        p_vel.add_mesh(self.active_grid, color="lightgrey", opacity=0.3, show_edges=False)
        
        # Create Glyphs (Arrows)
        arrows = self.active_grid.glyph(orient="Velocity", scale="Velocity", factor=0.1)
        p_vel.add_mesh(arrows, scalars="Pressure", cmap="jet", show_scalar_bar=False)

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