import sys
import os
import shutil
import subprocess
import threading
import time
import re
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, 
                             QVBoxLayout, QWidget, QGroupBox, QFormLayout, 
                             QDoubleSpinBox, QSpinBox, QComboBox, QLabel, QSplitter, 
                             QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QTabWidget, QMenu, QToolBar, QMessageBox, QLineEdit, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
from pyvistaqt import QtInteractor
import pyvista as pv
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# --- OpenFOAM IO & Case Management ---
class OpenFOAMCase:
    def __init__(self, case_dir=None):
        self.case_dir = case_dir
        self.control_dict = {}
        self.transport_props = {}
        
        if self.case_dir:
            self.read_configs()

    def generate_dummy_case(self, target_dir):
        """Generates a standard 'cavity' tutorial case for testing."""
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        os.makedirs(target_dir)
        
        # Create directories
        for d in ['0', 'constant', 'system']:
            os.makedirs(os.path.join(target_dir, d))
            
        # Write minimal controlDict
        with open(os.path.join(target_dir, 'system', 'controlDict'), 'w') as f:
            f.write("""
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application icoFoam;
startFrom startTime;
startTime 0;
stopAt endTime;
endTime 10;
deltaT 0.05;
writeControl timeStep;
writeInterval 20;
purgeWrite 0;
writeFormat ascii;
writePrecision 6;
writeCompression off;
timeFormat general;
timePrecision 6;
runTimeModifiable true;
""")
        
        # Write blockMeshDict
        with open(os.path.join(target_dir, 'system', 'blockMeshDict'), 'w') as f:
            f.write("""
FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }
convertToMeters 0.1;
vertices (
    (0 0 0) (1 0 0) (1 1 0) (0 1 0)
    (0 0 0.1) (1 0 0.1) (1 1 0.1) (0 1 0.1)
);
blocks ( hex (0 1 2 3 4 5 6 7) (20 20 1) simpleGrading (1 1 1) );
edges ();
boundary (
    ( movingWall { type wall; faces ( (3 7 6 2) ); } )
    ( fixedWalls { type wall; faces ( (0 4 7 3) (2 6 5 1) (1 5 4 0) ); } )
    ( frontAndBack { type empty; faces ( (0 3 2 1) (4 5 6 7) ); } )
);
mergePatchPairs ();
""")

        # Write transportProperties
        with open(os.path.join(target_dir, 'constant', 'transportProperties'), 'w') as f:
            f.write("""
FoamFile { version 2.0; format ascii; class dictionary; object transportProperties; }
transportModel Newtonian;
nu              [0 2 -1 0 0 0 0] 0.01;
""")

        # Write 0/U
        with open(os.path.join(target_dir, '0', 'U'), 'w') as f:
            f.write("""
FoamFile { version 2.0; format ascii; class volVectorField; object U; }
dimensions [0 1 -1 0 0 0 0];
internalField uniform (0 0 0);
boundaryField {
    movingWall { type fixedValue; value uniform (1 0 0); }
    fixedWalls { type noSlip; }
    frontAndBack { type empty; }
}
""")
        
        # Write 0/p
        with open(os.path.join(target_dir, '0', 'p'), 'w') as f:
            f.write("""
FoamFile { version 2.0; format ascii; class volScalarField; object p; }
dimensions [0 2 -2 0 0 0 0];
internalField uniform 0;
boundaryField {
    movingWall { type zeroGradient; }
    fixedWalls { type zeroGradient; }
    frontAndBack { type empty; }
}
""")
        
        # Run blockMesh
        try:
            subprocess.run(["blockMesh"], cwd=target_dir, check=True, shell=True)
            self.case_dir = target_dir
            self.read_configs()
            return True
        except Exception as e:
            print(f"Error running blockMesh: {e}")
            return False

    def read_configs(self):
        """Simple Regex parsing for demo purposes."""
        cd_path = os.path.join(self.case_dir, 'system', 'controlDict')
        if os.path.exists(cd_path):
            with open(cd_path, 'r') as f:
                content = f.read()
                self.control_dict['endTime'] = self._extract_val(content, 'endTime')
                self.control_dict['deltaT'] = self._extract_val(content, 'deltaT')
                self.control_dict['writeInterval'] = self._extract_val(content, 'writeInterval')

        tp_path = os.path.join(self.case_dir, 'constant', 'transportProperties')
        if os.path.exists(tp_path):
            with open(tp_path, 'r') as f:
                content = f.read()
                self.transport_props['nu'] = self._extract_val(content, 'nu', is_scalar=True)

    def _extract_val(self, content, key, is_scalar=False):
        try:
            if is_scalar:
                # Matches "nu [ ... ] 0.01;" -> gets 0.01
                m = re.search(rf"{key}\s+\[.*?\]\s+([\d\.]+);", content)
            else:
                # Matches "endTime 10;"
                m = re.search(rf"{key}\s+([\d\.]+);", content)
            return float(m.group(1)) if m else 0.0
        except: return 0.0

    def update_config(self, file_type, key, value):
        """Updates files on disk."""
        path = ""
        if file_type == 'controlDict':
            path = os.path.join(self.case_dir, 'system', 'controlDict')
        elif file_type == 'transport':
            path = os.path.join(self.case_dir, 'constant', 'transportProperties')
            
        if os.path.exists(path):
            with open(path, 'r') as f: lines = f.readlines()
            
            new_lines = []
            for line in lines:
                if line.strip().startswith(key):
                    # Preserve structure, replace number
                    if file_type == 'transport':
                        # nu [0 2 -1 0 0 0 0] 0.01;
                        pre = line.split(']')[0] + '] '
                        new_lines.append(f"{pre}{value};\n")
                    else:
                        new_lines.append(f"{key} {value};\n")
                else:
                    new_lines.append(line)
            
            with open(path, 'w') as f: f.writelines(new_lines)


# --- Worker for icoFoam ---
class SolverWorker(QObject):
    update_residuals = pyqtSignal(dict)
    new_time_step = pyqtSignal(float)
    finished = pyqtSignal()
    log_message = pyqtSignal(str)

    def run(self, case_dir):
        cmd = "icoFoam" # Standard solver
        
        try:
            # Use shell=True for windows/linux compatibility with PATH
            process = subprocess.Popen(
                cmd, 
                cwd=case_dir,
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1,
                shell=True
            )
            
            for line in process.stdout:
                line = line.strip()
                if not line: continue
                self.log_message.emit(line)
                
                # Parse Time
                if line.startswith("Time ="):
                    try:
                        t = float(line.split('=')[1])
                        self.new_time_step.emit(t)
                    except: pass

                # Parse Residuals (icoFoam standard output)
                # "Solving for Ux, Initial residual = 1.0e-05, Final..."
                if "Solving for" in line:
                    try:
                        parts = line.split(',')
                        var_part = parts[0].split('for')[1].strip() # Ux, Uy, p
                        res_part = parts[1].split('=')[1].strip()   # 1.0e-05
                        
                        self.update_residuals.emit({
                            'var': var_part,
                            'val': float(res_part)
                        })
                    except: pass
            
            process.wait()
            self.finished.emit()
            
        except Exception as e:
            self.log_message.emit(f"CRITICAL ERROR: {str(e)}")
            self.finished.emit()


# --- Derived Parts ---
class DerivedPart:
    def __init__(self, name, ptype):
        self.name = name
        self.type = ptype
        self.params = {}

class SlicePart(DerivedPart):
    def __init__(self, name):
        super().__init__(name, "Plane Section")
        self.params = {'Origin': [0.5, 0.5, 0.05], 'Normal': [0.0, 1.0, 0.0]}

class IsoPart(DerivedPart):
    def __init__(self, name):
        super().__init__(name, "Iso-Surface")
        self.params = {'Field': 'p', 'Value': 0.0}


# --- GUI Components ---
class ResidualPlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 2), dpi=90)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_yscale('log')
        self.ax.grid(True, linestyle=':', alpha=0.6)
        
        self.history = {'Ux': [], 'Uy': [], 'p': []}
        self.counters = {'Ux': 0, 'Uy': 0, 'p': 0}

    def update_plot(self, res):
        var = res['var']
        val = res['val']
        
        if var in self.history:
            self.history[var].append(val)
            self.counters[var] += 1
            
            # Replot every few steps to save UI thread
            if self.counters[var] % 5 == 0:
                self.ax.clear()
                self.ax.set_yscale('log')
                self.ax.grid(True, linestyle=':')
                
                for v_name, data in self.history.items():
                    if data:
                        self.ax.plot(data, label=v_name, lw=1)
                
                self.ax.legend(loc='upper right', fontsize='small')
                self.canvas.draw()
    
    def clear(self):
        self.history = {'Ux': [], 'Uy': [], 'p': []}
        self.ax.clear()
        self.canvas.draw()

class StarOpenFOAMWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenFOAM v2506 GUI (STAR-CCM+ Style)")
        self.resize(1600, 950)
        
        self.case = None
        self.mesh_data = None # VTK Object
        self.derived_parts = {}
        self.scenes = {} 
        
        # --- UI Construction ---
        main_split = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(main_split)
        
        # LEFT: Tree & Props
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
        
        # CENTER: Scene Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        main_split.addWidget(self.tabs)
        
        # RIGHT: Output
        right_split = QSplitter(Qt.Orientation.Vertical)
        self.resid_widget = ResidualPlotWidget()
        right_split.addWidget(self.resid_widget)
        
        self.log = QTableWidget(0, 1)
        self.log.setHeaderLabels(["Log Output"])
        self.log.horizontalHeader().setStretchLastSection(True)
        right_split.addWidget(self.log)
        
        main_split.addWidget(right_split)
        main_split.setSizes([300, 1000, 300])
        
        # --- Init ---
        self.init_tree()
        self.create_scene("Geometry", "Mesh")
        self.create_scene("Pressure", "Scalar")
        self.create_scene("Velocity", "Vector")
        
        # --- Toolbar ---
        tb = self.addToolBar("Sim")
        tb.addAction("New Cavity Case").triggered.connect(self.new_cavity_case)
        tb.addAction("Load Case").triggered.connect(self.load_case)
        tb.addSeparator()
        tb.addAction("Run Solver").triggered.connect(self.run_solver)
        tb.addSeparator()
        tb.addAction("Reload Results").triggered.connect(self.reload_vtk)

    def init_tree(self):
        self.tree.clear()
        self.root = QTreeWidgetItem(self.tree, ["Simulation"])
        
        self.node_phys = QTreeWidgetItem(self.root, ["Physics"])
        QTreeWidgetItem(self.node_phys, ["Transport"])
        
        self.node_time = QTreeWidgetItem(self.root, ["Time & Control"])
        
        self.node_parts = QTreeWidgetItem(self.root, ["Derived Parts"])
        self.node_scenes = QTreeWidgetItem(self.root, ["Scenes"])
        
        self.root.setExpanded(True)
        self.node_parts.setExpanded(True)
        self.node_scenes.setExpanded(True)

    def tree_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item: return
        text = item.text(0)
        
        menu = QMenu()
        if text == "Derived Parts":
            menu.addAction("New Plane Section").triggered.connect(lambda: self.create_part("Slice"))
            menu.addAction("New Iso-Surface").triggered.connect(lambda: self.create_part("Iso"))
        menu.exec(self.tree.mapToGlobal(pos))

    # --- Case Management ---
    def new_cavity_case(self):
        d = QFileDialog.getExistingDirectory(self, "Select Directory for New Case")
        if d:
            case_path = os.path.join(d, "cavity_test")
            self.case = OpenFOAMCase()
            success = self.case.generate_dummy_case(case_path)
            if success:
                self.log_msg(f"Generated case at {case_path}")
                self.load_case_dir(case_path)
            else:
                QMessageBox.critical(self, "Error", "Failed to run blockMesh. Ensure OpenFOAM is sourced.")

    def load_case(self):
        d = QFileDialog.getExistingDirectory(self, "Select OpenFOAM Case Directory")
        if d:
            self.load_case_dir(d)

    def load_case_dir(self, path):
        self.case = OpenFOAMCase(path)
        self.setWindowTitle(f"OpenFOAM GUI - {path}")
        self.reload_vtk()
        self.log_msg("Case Loaded. Configuration read.")

    def reload_vtk(self):
        """Reads OpenFOAM data using PyVista's OpenFOAMReader."""
        if not self.case: return
        
        try:
            # Point to controlDict for reading
            cd = os.path.join(self.case.case_dir, 'system', 'controlDict')
            reader = pv.OpenFOAMReader(cd)
            
            # Set active time to latest
            times = reader.time_values
            if len(times) > 0:
                reader.set_active_time_value(times[-1])
                self.log_msg(f"Loaded Time: {times[-1]}")
                
            self.mesh_data = reader.read()
            
            # OpenFOAM reader returns MultiBlock. Extract internal mesh.
            if isinstance(self.mesh_data, pv.MultiBlock):
                # Usually block 0 is internalMesh
                self.mesh_data = self.mesh_data[0]
            
            self.update_scenes()
        except Exception as e:
            self.log_msg(f"VTK Load Error: {e}")

    # --- Solver ---
    def run_solver(self):
        if not self.case: return
        
        self.resid_widget.clear()
        self.worker = SolverWorker()
        self.thread = threading.Thread(target=self.worker.run, args=(self.case.case_dir,))
        
        self.worker.log_message.connect(self.log_msg)
        self.worker.update_residuals.connect(self.resid_widget.update_plot)
        self.worker.new_time_step.connect(self.on_time_step)
        self.worker.finished.connect(lambda: self.log_msg("Solver Finished."))
        
        self.thread.start()

    def on_time_step(self, t):
        # Optional: Auto-reload results periodically
        # self.reload_vtk() 
        pass

    # --- Visualization ---
    def create_scene(self, name, type_):
        plotter = QtInteractor(self.tabs)
        plotter.set_background("white")
        plotter.add_axes()
        idx = self.tabs.addTab(plotter.interactor, name)
        self.scenes[idx] = {'type': type_, 'plotter': plotter}

    def close_tab(self, idx):
        self.scenes[idx]['plotter'].close()
        del self.scenes[idx]
        self.tabs.removeTab(idx)

    def update_scenes(self):
        if self.mesh_data is None: return
        
        for idx, s in self.scenes.items():
            p = s['plotter']
            p.clear()
            
            if s['type'] == 'Mesh':
                p.add_mesh(self.mesh_data, show_edges=True, color="lightblue")
                
            elif s['type'] == 'Scalar':
                # Check for 'p' array
                if 'p' in self.mesh_data.point_data:
                    p.add_mesh(self.mesh_data, scalars='p', cmap='jet')
                elif 'p' in self.mesh_data.cell_data:
                    p.add_mesh(self.mesh_data, scalars='p', cmap='jet')
                    
            elif s['type'] == 'Vector':
                # Check for 'U'
                p.add_mesh(self.mesh_data, color="lightgrey", opacity=0.2, show_edges=True)
                if 'U' in self.mesh_data.point_data:
                    # Create Glyphs
                    self.mesh_data.set_active_vectors("U")
                    arrows = self.mesh_data.glyph(scale="U", factor=0.1)
                    p.add_mesh(arrows, color="black")

            # Add Derived Parts
            for name, part in self.derived_parts.items():
                self.draw_derived(p, part)

    def draw_derived(self, p, part):
        if self.mesh_data is None: return
        try:
            if isinstance(part, SlicePart):
                sliced = self.mesh_data.slice(normal=part.params['Normal'], origin=part.params['Origin'])
                p.add_mesh(sliced, scalars='p', cmap='jet', line_width=3)
            elif isinstance(part, IsoPart):
                iso = self.mesh_data.contour(scalars=part.params['Field'], isosurfaces=[part.params['Value']])
                p.add_mesh(iso, color='white', opacity=0.6)
        except: pass

    # --- Interaction ---
    def create_part(self, ptype):
        count = len(self.derived_parts) + 1
        name = f"{ptype} {count}"
        
        if ptype == "Slice": part = SlicePart(name)
        else: part = IsoPart(name)
        
        self.derived_parts[name] = part
        item = QTreeWidgetItem(self.node_parts, [name])
        item.setData(0, Qt.ItemDataRole.UserRole, part)
        self.tree.setCurrentItem(item)
        self.update_scenes()

    def on_tree_click(self, item, col):
        # Clear props
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        text = item.text(0)
        self.props_panel.setTitle(f"Properties: {text}")
        
        # Derived Parts
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(data, SlicePart):
            self.add_vec_edit("Origin", data.params['Origin'])
            self.add_vec_edit("Normal", data.params['Normal'])
        
        # Config Editing
        if text == "Time & Control" and self.case:
            self.add_cfg_edit("EndTime", "endTime", self.case.control_dict, 'controlDict')
            self.add_cfg_edit("DeltaT", "deltaT", self.case.control_dict, 'controlDict')
            
        if text == "Transport" and self.case:
             self.add_cfg_edit("Viscosity (nu)", "nu", self.case.transport_props, 'transport')

    def add_cfg_edit(self, label, key, source_dict, file_type):
        sb = QDoubleSpinBox()
        sb.setRange(0, 10000)
        sb.setDecimals(5)
        val = source_dict.get(key, 0.0)
        sb.setValue(val)
        
        def update_val(v):
            source_dict[key] = v
            self.case.update_config(file_type, key, v)
            
        sb.valueChanged.connect(update_val)
        self.props_layout.addRow(label, sb)

    def add_vec_edit(self, label, vec):
        # Helper for vector input
        for i, axis in enumerate(['X', 'Y', 'Z']):
            sb = QDoubleSpinBox()
            sb.setRange(-10, 10)
            sb.setSingleStep(0.1)
            sb.setValue(vec[i])
            sb.valueChanged.connect(lambda v, idx=i: vec.__setitem__(idx, v) or self.update_scenes())
            self.props_layout.addRow(f"{label} {axis}", sb)

    def log_msg(self, msg):
        r = self.log.rowCount()
        self.log.insertRow(r)
        self.log.setItem(r, 0, QTableWidgetItem(msg))
        self.log.scrollToBottom()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StarOpenFOAMWindow()
    window.show()
    sys.exit(app.exec())