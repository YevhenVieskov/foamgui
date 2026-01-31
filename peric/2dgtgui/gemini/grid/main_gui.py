import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDockWidget, QTreeWidget, 
                             QTreeWidgetItem, QVBoxLayout, QWidget, QGroupBox, 
                             QFormLayout, QSpinBox, QComboBox, QPushButton, QLabel, 
                             QSplitter, QFrame, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from pyvistaqt import QtInteractor
import pyvista as pv

from grid_engine import GridEngine

class StarCCMGridGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCAFFA Grid Generator (STAR-CCM+ Style)")
        self.resize(1200, 800)
        
        self.engine = GridEngine()
        self.mesh_actor = None

        # --- Main Layout (Splitter) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # --- Left Panel: Simulation Tree & Properties ---
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_panel.setLayout(left_layout)
        
        # 1. Simulation Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Simulation Tree")
        self.tree.itemClicked.connect(self.on_tree_click)
        left_layout.addWidget(self.tree, stretch=1)
        
        # Populate Tree
        self.root_node = QTreeWidgetItem(self.tree, ["Grid Model"])
        self.params_node = QTreeWidgetItem(self.root_node, ["Parameters"])
        self.boundary_node = QTreeWidgetItem(self.root_node, ["Boundaries"])
        self.south_node = QTreeWidgetItem(self.boundary_node, ["South"])
        self.north_node = QTreeWidgetItem(self.boundary_node, ["North"])
        self.west_node = QTreeWidgetItem(self.boundary_node, ["West"])
        self.east_node = QTreeWidgetItem(self.boundary_node, ["East"])
        self.root_node.setExpanded(True)
        self.boundary_node.setExpanded(True)

        # 2. Properties Panel (Dynamic)
        self.props_group = QGroupBox("Properties")
        self.props_layout = QFormLayout()
        self.props_group.setLayout(self.props_layout)
        left_layout.addWidget(self.props_group, stretch=1)

        splitter.addWidget(left_panel)

        # --- Right Panel: 3D Visualization (PyVista) ---
        self.plotter = QtInteractor(self)
        self.plotter.set_background("white")  # Star-CCM+ usually has light gradient or white
        self.plotter.add_axes()
        splitter.addWidget(self.plotter.interactor)
        
        # Set initial splitter sizes
        splitter.setSizes([300, 900])

        # Status Bar
        self.statusBar().showMessage("Ready. Select 'Parameters' in the tree to begin.")

        # Toolbar
        toolbar = self.addToolBar("Main")
        gen_action = toolbar.addAction("Generate Mesh")
        gen_action.triggered.connect(self.generate_mesh)
        save_action = toolbar.addAction("Save .grd")
        save_action.triggered.connect(self.save_mesh)

        # Initial View
        self.show_parameters_ui()

    def on_tree_click(self, item, col):
        """Updates the Properties panel based on selection."""
        # Clear current properties
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        text = item.text(0)
        self.props_group.setTitle(f"Properties: {text}")

        if text == "Parameters":
            self.show_parameters_ui()
        elif text in ["South", "North", "West", "East"]:
            self.show_boundary_ui(text)
        elif text == "Grid Model":
            btn = QPushButton("Generate Grid")
            btn.clicked.connect(self.generate_mesh)
            self.props_layout.addRow(btn)

    def show_parameters_ui(self):
        [cite_start]"""UI for Global Parameters (NGR, IDIR, NICV, NJCV)[cite: 46, 56]."""
        
        # Grid Levels (NGR)
        self.spin_ngr = QSpinBox()
        self.spin_ngr.setRange(1, 5)
        self.spin_ngr.setValue(self.engine.ngr)
        self.props_layout.addRow("Grid Levels (NGR):", self.spin_ngr)

        # Direction (IDIR)
        self.combo_idir = QComboBox()
        self.combo_idir.addItems(["0: South-North", "1: West-East"])
        self.combo_idir.setCurrentIndex(self.engine.idir)
        self.props_layout.addRow("Line Direction (IDIR):", self.combo_idir)

        # Cells in I (NICV)
        self.spin_nicv = QSpinBox()
        self.spin_nicv.setRange(2, 1000)
        self.spin_nicv.setValue(self.engine.nicv)
        self.props_layout.addRow("I-Direction Cells (NICV):", self.spin_nicv)

        # Cells in J (NJCV)
        self.spin_njcv = QSpinBox()
        self.spin_njcv.setRange(2, 1000)
        self.spin_njcv.setValue(self.engine.njcv)
        self.props_layout.addRow("J-Direction Cells (NJCV):", self.spin_njcv)

        # Apply Button
        btn_apply = QPushButton("Apply Parameters")
        btn_apply.clicked.connect(self.apply_parameters)
        self.props_layout.addRow(btn_apply)

    def show_boundary_ui(self, name):
        [cite_start]"""UI for Boundary definitions (Lines/Segments)[cite: 58, 60]."""
        lbl_info = QLabel(f"Define geometry for {name} boundary.")
        self.props_layout.addRow(lbl_info)
        
        # Example input for line segments
        spin_segments = QSpinBox()
        spin_segments.setValue(1)
        self.props_layout.addRow("Number of Lines:", spin_segments)
        
        # Boundary Type
        combo_type = QComboBox()
        combo_type.addItems(["Wall", "Inlet", "Outlet", "Symmetry"])
        self.props_layout.addRow("Boundary Type:", combo_type)
        
        btn_set = QPushButton(f"Set {name} Data")
        self.props_layout.addRow(btn_set)

    def apply_parameters(self):
        """Updates the engine with values from UI."""
        ngr = self.spin_ngr.value()
        idir = self.combo_idir.currentIndex()
        nicv = self.spin_nicv.value()
        njcv = self.spin_njcv.value()
        
        self.engine.set_control_params(ngr, idir, nicv, njcv)
        self.statusBar().showMessage(f"Parameters updated: NICV={nicv}, NJCV={njcv}")

    def generate_mesh(self):
        """Calls engine to generate mesh and visualizes it."""
        try:
            xx, yy, zz = self.engine.generate_grid()
            
            # Create PyVista StructuredGrid
            grid = pv.StructuredGrid(xx, yy, zz)
            
            # Visualization
            if self.mesh_actor:
                self.plotter.remove_actor(self.mesh_actor)
            
            self.mesh_actor = self.plotter.add_mesh(
                grid, 
                show_edges=True, 
                color="lightblue", 
                line_width=2,
                edge_color="black"
            )
            self.plotter.reset_camera()
            self.statusBar().showMessage("Mesh generated successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def save_mesh(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Grid File", "", "Grid Files (*.grd)")
        if filename:
            self.engine.save_grid_file(filename)
            self.statusBar().showMessage(f"Saved to {filename}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StarCCMGridGUI()
    window.show()
    sys.exit(app.exec())