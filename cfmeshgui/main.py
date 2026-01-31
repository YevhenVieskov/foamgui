import sys
import os
import vtk
import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QTableWidget, 
                             QTableWidgetItem, QSplitter, QTextEdit, QPushButton, 
                             QHeaderView, QLabel, QFileDialog, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QProcess, QTimer

# --- 1. Validation Logic ---
class MeshDictValidator:
    """Validates the integrity of the mesh parameters."""
    
    @staticmethod
    def validate(config):
        errors = []
        
        # Check Max Cell Size
        max_cell = config.get("maxCellSize")
        if not isinstance(max_cell, (int, float)) or max_cell <= 0:
            errors.append("maxCellSize must be a positive number.")
            
        # Check Boundary Layers
        if "boundaryLayers" in config:
            layers = config["boundaryLayers"]
            if layers.get("nLayers", 0) < 0:
                errors.append("nLayers cannot be negative.")
                
        # Check Surfaces exist (Mock check)
        if "surfaceFile" in config:
            if not config["surfaceFile"].endswith(".stl") and not config["surfaceFile"].endswith(".fms"):
                errors.append("surfaceFile must be an STL or FMS file.")

        return len(errors) == 0, errors

# --- 2. The Main GUI ---
class OpenFoamGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("cfMesh GUI - OpenFOAM 2506 (Star-CCM+ Style)")
        self.resize(1400, 900)
        
        # Internal Data Structure (representing meshDict)
        self.mesh_data = {
            "Global Settings": {
                "surfaceFile": "geometry.stl",
                "maxCellSize": 1.0,
                "boundaryCellSize": 0.5,
                "minCellSize": 0.1
            },
            "Boundary Layers": {
                "nLayers": 3,
                "thicknessRatio": 1.2,
                "maxThickness": 0.5
            },
            "Local Refinement": {
                "refinementThickness": 0.2,
                "refinementLevel": 2
            }
        }

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.setup_ui()

    def setup_ui(self):
        # Main Layout using Splitters for Resizability
        main_splitter = QSplitter(Qt.Horizontal)
        left_splitter = QSplitter(Qt.Vertical)
        
        # --- Left Panel: Tree & Properties ---
        # 1. Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Simulation Tree")
        self.populate_tree()
        self.tree.itemClicked.connect(self.on_tree_click)
        
        # 2. Properties Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemChanged.connect(self.on_table_edit)
        
        left_splitter.addWidget(self.tree)
        left_splitter.addWidget(self.table)
        left_splitter.setStretchFactor(0, 1)
        left_splitter.setStretchFactor(1, 1)

        # --- Center Panel: 3D View & Logs ---
        center_splitter = QSplitter(Qt.Vertical)
        
        # 3. PyVista 3D Viewport
        self.plotter = BackgroundPlotter(show=False)
        self.plotter.add_text("Viewport", position='upper_left', font_size=10)
        self.plotter.show_grid()
        self.clip_active = False
        
        # 4. Log Viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Monospace;")
        self.log_viewer.setPlaceholderText("OpenFOAM Log Output...")
        
        center_splitter.addWidget(self.plotter)
        center_splitter.addWidget(self.log_viewer)
        center_splitter.setStretchFactor(0, 3) # Viewport is larger
        center_splitter.setStretchFactor(1, 1) # Log is smaller

        # --- Right Panel: Actions ---
        action_panel = QFrame()
        action_layout = QVBoxLayout()
        
        btn_load = QPushButton("Load STL")
        btn_load.clicked.connect(self.load_geometry)
        
        btn_validate = QPushButton("Validate meshDict")
        btn_validate.clicked.connect(self.run_validation)
        
        btn_run = QPushButton("Run cfMesh")
        btn_run.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        btn_run.clicked.connect(self.run_meshing)
        
        btn_clip = QPushButton("Toggle Clip Plane")
        btn_clip.clicked.connect(self.toggle_clipping)
        
        action_layout.addWidget(QLabel("<b>Actions</b>"))
        action_layout.addWidget(btn_load)
        action_layout.addWidget(btn_clip)
        action_layout.addWidget(btn_validate)
        action_layout.addStretch()
        action_layout.addWidget(btn_run)
        action_panel.setLayout(action_layout)
        action_panel.setFixedWidth(150)

        # Add to Main Splitter
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(center_splitter)
        main_splitter.addWidget(action_panel)
        main_splitter.setStretchFactor(1, 4)

        self.setCentralWidget(main_splitter)
        
        # Initialize default 3D object
        self.mesh_actor = None
        self.mesh_dataset = None

    # --- Logic: Tree & Parser ---
    def populate_tree(self):
        self.tree.clear()
        for category in self.mesh_data:
            item = QTreeWidgetItem([category])
            self.tree.addTopLevelItem(item)

    def on_tree_click(self, item, column):
        """Parser: Automatically populates QTableWidget based on node."""
        category = item.text(0)
        if category in self.mesh_data:
            data = self.mesh_data[category]
            self.table.setRowCount(len(data))
            self.table.blockSignals(True) # Prevent triggering update while populating
            
            for row, (key, value) in enumerate(data.items()):
                self.table.setItem(row, 0, QTableWidgetItem(str(key)))
                self.table.setItem(row, 1, QTableWidgetItem(str(value)))
                # Make key read-only
                self.table.item(row, 0).setFlags(Qt.ItemIsEnabled)
            
            self.table.blockSignals(False)

    def on_table_edit(self, item):
        """Updates internal dictionary when table is edited."""
        row = item.row()
        key = self.table.item(row, 0).text()
        value = item.text()
        
        current_category = self.tree.currentItem().text(0)
        
        # Simple type conversion (try float, int, then string)
        try:
            if "." in value:
                val_conv = float(value)
            else:
                val_conv = int(value)
        except ValueError:
            val_conv = value
            
        self.mesh_data[current_category][key] = val_conv

    # --- Logic: Validation ---
    def run_validation(self):
        # Flatten dict for validation (simplified)
        flat_config = {}
        for cat in self.mesh_data.values():
            flat_config.update(cat)
            
        is_valid, errors = MeshDictValidator.validate(flat_config)
        
        if is_valid:
            QMessageBox.information(self, "Validation", "meshDict is Valid!")
        else:
            QMessageBox.warning(self, "Validation Failed", "\n".join(errors))

    # --- Logic: 3D Visualization & Clipping ---
    def load_geometry(self):
        # For demo purposes, we generate a sample mesh if no file selected
        # file_path, _ = QFileDialog.getOpenFileName(self, "Open Geometry", "", "STL Files (*.stl)")
        
        # Creating a sample generic PyVista mesh (Dragon-like or Cube)
        self.log_viewer.append("Loading geometry...")
        self.mesh_dataset = pv.Cube() 
        
        self.plotter.clear()
        self.mesh_actor = self.plotter.add_mesh(self.mesh_dataset, color='lightblue', show_edges=True)
        self.plotter.reset_camera()

    def toggle_clipping(self):
        if not self.mesh_dataset:
            return

        self.plotter.clear()
        if not self.clip_active:
            # Enable widget clipping
            self.plotter.add_mesh_clip_plane(self.mesh_dataset, show_edges=True)
            self.clip_active = True
            self.log_viewer.append("Clipping Enabled.")
        else:
            # Reset to normal
            self.plotter.add_mesh(self.mesh_dataset, color='lightblue', show_edges=True)
            self.clip_active = False
            self.log_viewer.append("Clipping Disabled.")

    # --- Logic: Process & Log Viewer ---
    def run_meshing(self):
        self.log_viewer.clear()
        self.log_viewer.append("Starting cfMesh (simulation)...")
        
        # NOTE: Since we cannot run actual OpenFOAM here, we start a mock script
        # In production, replace with: self.process.start("cartesianMesh")
        
        cmd = "python -c \"import time; print('Reading surface...'); time.sleep(0.5); print('Refining...'); time.sleep(0.5); print('Meshing finished.');\""
        self.process.start(cmd)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.log_viewer.append(stdout)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.log_viewer.append(f"<span style='color:red'>{stderr}</span>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OpenFoamGUI()
    window.show()
    sys.exit(app.exec_())