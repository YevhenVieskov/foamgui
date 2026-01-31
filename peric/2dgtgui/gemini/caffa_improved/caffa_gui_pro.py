import sys
import subprocess
import threading
import time
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, 
                             QVBoxLayout, QWidget, QGroupBox, QFormLayout, 
                             QDoubleSpinBox, QSpinBox, QComboBox, QLabel, QSplitter, 
                             QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QTabWidget, QMenu, QToolBar, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QAction, QIcon
from pyvistaqt import QtInteractor
import pyvista as pv

# Matplotlib for Residuals
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# --- IO / Mock Physics Engine ---
class CaffaPhysicsEngine:
    """Handles Grid Import and Mock Physics Generation"""
    def generate_dummy_grid(self):
        # Generate a structured grid (C-Grid like)
        ni, nj = 80, 40
        x = np.linspace(0, 8, ni)
        y = np.linspace(0, 4, nj)
        xx, yy = np.meshgrid(x, y, indexing='ij')
        zz = np.zeros_like(xx)
        grid = pv.StructuredGrid(xx, yy, zz)
        return grid

    def import_grid(self, filename):
        # Placeholder for real binary reader
        return self.generate_dummy_grid()

# --- Worker for Live Solver ---
class SolverWorker(QObject):
    update_residuals = pyqtSignal(dict)
    update_fields = pyqtSignal(dict) 
    finished = pyqtSignal()
    log_message = pyqtSignal(str)

    def run(self):
        """Simulates a Vortex Shedding process"""
        # Physics Grid (Internal)
        ni, nj = 80, 40
        x = np.linspace(0, 8, ni)
        y = np.linspace(0, 4, nj)
        xx, yy = np.meshgrid(x, y, indexing='ij')
        
        for t in range(1, 500):
            if threading.current_thread().is_interrupted: break
            time.sleep(0.05) 
            
            # 1. Physics: Travelling Wave (Vortex Street Mock)
            freq = 2.0
            phase = t * 0.1
            
            # Pressure field (High/Low pressure blobs moving)
            p_field = np.sin(xx - phase) * np.cos(yy * freq)
            
            # Velocity field (Perturbed channel flow)
            u_base = 1.0 - (yy - 2)**2 / 4.0 # Parabolic
            u_pert = -0.5 * np.cos(xx - phase) * np.sin(yy * freq)
            v_pert = 0.5 * np.sin(xx - phase) * np.cos(yy * freq)
            
            u_final = u_base + u_pert
            v_final = v_pert
            
            # 2. Emit Data
            field_data = {
                'iter': t,
                'Pressure': p_field.flatten(order='F'),
                'Velocity_X': u_final.flatten(order='F'),
                'Velocity_Y': v_final.flatten(order='F')
            }
            
            res = {
                'iter': t,
                'U': 10**(-3 - np.sin(t*0.01)),
                'V': 10**(-3 - np.cos(t*0.01)),
                'P': 10**(-2 - 0.5*np.sin(t*0.05))
            }
            
            self.update_fields.emit(field_data)
            self.update_residuals.emit(res)
            self.log_message.emit(f"ITER {t} | SOLVING MOMENTUM EQUATIONS...")
        
        self.finished.emit()

# --- Derived Parts Classes ---
class DerivedPart:
    def __init__(self, name, type_):
        self.name = name
        self.type = type_
        self.params = {} 

class SlicePart(DerivedPart):
    def __init__(self, name):
        super().__init__(name, "Plane Section")
        self.params = {'Origin': [4.0, 2.0, 0.0], 'Normal': [1.0, 0.0, 0.0]}

class IsoPart(DerivedPart):
    def __init__(self, name):
        super().__init__(name, "Iso-Surface")
        self.params = {'Field': 'Pressure', 'Value': 0.0}

class StreamlinePart(DerivedPart):
    def __init__(self, name):
        super().__init__(name, "Streamlines")
        self.params = {'Source Radius': 2.0, 'Points': 50}

# --- GUI Components ---

class ResidualPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 2), dpi=90)
        self.figure.patch.set_facecolor('#ffffff')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_yscale('log')
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.data = {'iter': [], 'U': [], 'V': [], 'P': []}

    def update_plot(self, res):
        self.data['iter'].append(res['iter'])
        self.data['U'].append(res['U'])
        self.data['V'].append(res['V'])
        self.data['P'].append(res['P'])
        
        self.ax.clear()
        self.ax.set_yscale('log')
        self.ax.grid(True, linestyle=':')
        self.ax.plot(self.data['iter'], self.data['U'], label='U', lw=1)
        self.ax.plot(self.data['iter'], self.data['V'], label='V', lw=1)
        self.ax.plot(self.data['iter'], self.data['P'], label='P', lw=1)
        self.ax.legend(loc='upper right', fontsize='small')
        self.canvas.draw()

    def clear(self):
        self.data = {'iter': [], 'U': [], 'V': [], 'P': []}
        self.ax.clear()
        self.canvas.draw()

class StarCCMWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCAFFA STAR-CCM+ Clone")
        self.resize(1800, 1000)
        
        self.physics = CaffaPhysicsEngine()
        self.base_grid = self.physics.generate_dummy_grid()
        self.derived_parts = {} # name -> obj
        self.scenes = {} # tab_index -> scene_config
        
        # --- UI Layout ---
        main_split = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_split)
        
        # LEFT: Simulation Tree & Props
        left_split = QSplitter(Qt.Orientation.Vertical)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Simulation")
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.tree_context_menu)
        self.tree.itemClicked.connect(self.on_tree_click)
        left_split.addWidget(self.tree)
        
        self.props_panel = QGroupBox("Properties")
        self.props_layout = QFormLayout()
        self.props_panel.setLayout(self.props_layout)
        left_split.addWidget(self.props_panel)
        main_split.addWidget(left_split)
        
        # CENTER: Scenes
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        main_split.addWidget(self.tabs)
        
        # RIGHT: Residuals & Output
        right_split = QSplitter(Qt.Orientation.Vertical)
        self.resid_widget = ResidualPlotWidget()
        right_split.addWidget(self.resid_widget)
        
        self.log = QTableWidget(0, 1)
        self.log.setHeaderLabels(["Output"])
        self.log.horizontalHeader().setStretchLastSection(True)
        right_split.addWidget(self.log)
        main_split.addWidget(right_split)
        
        main_split.setSizes([300, 1100, 400])

        # --- Init Tree ---
        self.init_tree()
        
        # --- Create Default Scenes ---
        self.create_scene("Geometry", "Mesh")
        self.create_scene("Scalar Scene 1", "Scalar")
        
        # --- Toolbar ---
        tb = self.addToolBar("Sim")
        tb.addAction("Run").triggered.connect(self.start_solver)
        tb.addAction("Stop").triggered.connect(self.stop_solver)
        tb.addSeparator()
        tb.addAction("Reset View").triggered.connect(self.reset_views)

    def init_tree(self):
        self.root = QTreeWidgetItem(self.tree, ["Simulation"])
        
        self.node_parts = QTreeWidgetItem(self.root, ["Derived Parts"])
        self.node_scenes = QTreeWidgetItem(self.root, ["Scenes"])
        
        self.root.setExpanded(True)
        self.node_parts.setExpanded(True)
        self.node_scenes.setExpanded(True)

    def tree_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item: return
        
        menu = QMenu()
        text = item.text(0)
        
        if text == "Derived Parts":
            menu.addAction("New Plane Section").triggered.connect(lambda: self.create_derived_part("Slice"))
            menu.addAction("New Iso-Surface").triggered.connect(lambda: self.create_derived_part("Iso"))
            menu.addAction("New Streamline").triggered.connect(lambda: self.create_derived_part("Stream"))
        elif text == "Scenes":
            menu.addAction("New Scalar Scene").triggered.connect(lambda: self.create_scene("New Scalar", "Scalar"))
            menu.addAction("New Vector Scene").triggered.connect(lambda: self.create_scene("New Vector", "Vector"))
        
        menu.exec(self.tree.mapToGlobal(pos))

    # --- Scene Management ---
    def create_scene(self, name, type_):
        plotter = QtInteractor(self.tabs)
        plotter.set_background("white")
        plotter.add_axes()
        
        # Initialize with Base Grid
        if type_ == "Mesh":
            plotter.add_mesh(self.base_grid, show_edges=True, color="lightblue")
        elif type_ == "Scalar":
            plotter.add_mesh(self.base_grid, scalars=None, cmap="jet", show_edges=False)
        elif type_ == "Vector":
            # Add Glyphs container
            plotter.add_mesh(self.base_grid, color="white", opacity=0.1) # Ghost mesh
        
        idx = self.tabs.addTab(plotter.interactor, name)
        self.scenes[idx] = {'type': type_, 'plotter': plotter}
        
        # Add to Tree
        QTreeWidgetItem(self.node_scenes, [name])

    def close_tab(self, idx):
        plotter = self.scenes[idx]['plotter']
        plotter.close()
        del self.scenes[idx]
        self.tabs.removeTab(idx)

    # --- Derived Parts Logic ---
    def create_derived_part(self, ptype):
        count = self.node_parts.childCount() + 1
        name = f"{ptype} {count}"
        
        if ptype == "Slice":
            part = SlicePart(name)
        elif ptype == "Iso":
            part = IsoPart(name)
        elif ptype == "Stream":
            part = StreamlinePart(name)
            
        self.derived_parts[name] = part
        item = QTreeWidgetItem(self.node_parts, [name])
        item.setData(0, Qt.ItemDataRole.UserRole, part)
        self.tree.setCurrentItem(item)
        self.on_tree_click(item, 0) # Show props

    def update_derived_viz(self):
        """Re-generates derived parts on active scenes."""
        # Simple implementation: Add derived parts to current active tab if it's a 3D view
        idx = self.tabs.currentIndex()
        if idx not in self.scenes: return
        
        plotter = self.scenes[idx]['plotter']
        # Clear previous derived actors (Optimization needed for prod)
        # Here we rely on live update loop to redraw everything

    # --- Properties Editor ---
    def on_tree_click(self, item, col):
        # Clear props
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        data = item.data(0, Qt.ItemDataRole.UserRole)
        
        if isinstance(data, SlicePart):
            self.build_slice_props(data)
        elif isinstance(data, IsoPart):
            self.build_iso_props(data)
        elif isinstance(data, StreamlinePart):
            self.build_stream_props(data)

    def build_slice_props(self, part):
        self.add_double_vec("Origin", part.params['Origin'])
        self.add_double_vec("Normal", part.params['Normal'])

    def build_iso_props(self, part):
        cb = QComboBox()
        cb.addItems(["Pressure", "Velocity_X"])
        cb.setCurrentText(part.params['Field'])
        cb.currentTextChanged.connect(lambda t: part.params.update({'Field': t}))
        self.props_layout.addRow("Field:", cb)
        
        sb = QDoubleSpinBox()
        sb.setValue(part.params['Value'])
        sb.valueChanged.connect(lambda v: part.params.update({'Value': v}))
        self.props_layout.addRow("Iso Value:", sb)

    def build_stream_props(self, part):
        sb = QSpinBox()
        sb.setValue(part.params['Points'])
        sb.valueChanged.connect(lambda v: part.params.update({'Points': v}))
        self.props_layout.addRow("Seed Points:", sb)

    def add_double_vec(self, label, vec):
        # Simple vector editor helper
        hbox = QWidget()
        layout = QVBoxLayout()
        hbox.setLayout(layout)
        
        for i, axis in enumerate(['X', 'Y', 'Z']):
            sb = QDoubleSpinBox()
            sb.setRange(-100, 100)
            sb.setValue(vec[i])
            # Python closure hack for i
            sb.valueChanged.connect(lambda v, idx=i: vec.__setitem__(idx, v))
            self.props_layout.addRow(f"{label} {axis}:", sb)

    # --- Solver & Live Update ---
    def start_solver(self):
        self.resid_widget.clear()
        self.log.setRowCount(0)
        
        threading.current_thread().is_interrupted = False
        self.worker = SolverWorker()
        self.thread = threading.Thread(target=self.worker.run)
        
        self.worker.update_fields.connect(self.update_live_scenes)
        self.worker.update_residuals.connect(self.resid_widget.update_plot)
        self.worker.log_message.connect(self.log_msg)
        
        self.thread.start()

    def stop_solver(self):
        threading.current_thread().is_interrupted = True

    def update_live_scenes(self, data):
        """Core Visualization Loop"""
        # 1. Update Base Grid Data
        self.base_grid.point_data["Pressure"] = data['Pressure']
        u, v = data['Velocity_X'], data['Velocity_Y']
        w = np.zeros_like(u)
        self.base_grid.point_data["Velocity"] = np.column_stack((u, v, w))
        
        # 2. Iterate over all open Scenes
        for idx, scene in self.scenes.items():
            plotter = scene['plotter']
            stype = scene['type']
            
            # Optimization: Only full redraw if strictly necessary, otherwise update scalars
            # For this demo, we do a clean redraw to support dynamic derived parts
            plotter.clear()
            
            # Draw Base Mesh Context
            if stype == "Scalar":
                plotter.add_mesh(self.base_grid, scalars="Pressure", cmap="jet", show_edges=False, show_scalar_bar=True)
            elif stype == "Vector":
                 plotter.add_mesh(self.base_grid, color="white", opacity=0.1, show_edges=False)
                 arrows = self.base_grid.glyph(orient="Velocity", scale="Velocity", factor=0.2)
                 plotter.add_mesh(arrows, color="black")

            # Draw Derived Parts
            for name, part in self.derived_parts.items():
                if isinstance(part, SlicePart):
                    try:
                        sliced = self.base_grid.slice(normal=part.params['Normal'], origin=part.params['Origin'])
                        plotter.add_mesh(sliced, scalars="Pressure", cmap="jet", line_width=2)
                    except: pass
                elif isinstance(part, IsoPart):
                    try:
                        iso = self.base_grid.contour(isosurfaces=1, scalars=part.params['Field'], rng=[part.params['Value'], part.params['Value']])
                        plotter.add_mesh(iso, color="white", opacity=0.5)
                    except: pass
                elif isinstance(part, StreamlinePart):
                    try:
                        streams = self.base_grid.streamlines(vectors="Velocity", n_points=part.params['Points'], source_radius=part.params['Source Radius'])
                        plotter.add_mesh(streams, color="black", line_width=1)
                    except: pass

    def log_msg(self, msg):
        r = self.log.rowCount()
        self.log.insertRow(r)
        self.log.setItem(r, 0, QTableWidgetItem(msg))
        self.log.scrollToBottom()

    def reset_views(self):
        for idx, scene in self.scenes.items():
            scene['plotter'].reset_camera()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StarCCMWindow()
    window.show()
    sys.exit(app.exec())