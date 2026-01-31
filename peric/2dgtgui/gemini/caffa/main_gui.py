import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDockWidget, QTreeWidget, 
                             QTreeWidgetItem, QVBoxLayout, QWidget, QGroupBox, 
                             QFormLayout, QDoubleSpinBox, QSpinBox, QComboBox, 
                             QPushButton, QLabel, QSplitter, QFileDialog, QCheckBox, 
                             QMessageBox, QToolBar)
from PyQt6.QtCore import Qt
from pyvistaqt import QtInteractor
import pyvista as pv

from caffa_engine import CaffaCase

class CaffaGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyCAFFA - CFD Solver Interface")
        self.resize(1280, 800)
        
        self.case = CaffaCase()
        self.solution_mesh = None

        # --- Main Layout ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # --- Left Panel: Simulation Tree ---
        left_container = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_container.setLayout(left_layout)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Simulation")
        self.tree.itemClicked.connect(self.on_tree_click)
        left_layout.addWidget(self.tree)
        
        # Build Tree Nodes
        self.root = QTreeWidgetItem(self.tree, [self.case.title])
        
        self.node_models = QTreeWidgetItem(self.root, ["Physics Models"])
        self.node_material = QTreeWidgetItem(self.root, ["Material Properties"])
        self.node_initial = QTreeWidgetItem(self.root, ["Initial Conditions"])
        self.node_numerics = QTreeWidgetItem(self.root, ["Numerics & Solvers"])
        self.node_time = QTreeWidgetItem(self.root, ["Time Settings"])
        self.node_run = QTreeWidgetItem(self.root, ["Run Simulation"])
        
        self.root.setExpanded(True)
        splitter.addWidget(left_container)

        # --- Middle Panel: Properties ---
        self.props_group = QGroupBox("Properties")
        self.props_layout = QFormLayout()
        self.props_group.setLayout(self.props_layout)
        
        props_container = QWidget()
        props_vbox = QVBoxLayout()
        props_vbox.addWidget(self.props_group)
        props_vbox.addStretch()
        props_container.setLayout(props_vbox)
        
        splitter.addWidget(props_container)

        # --- Right Panel: Visualization (PyVista) ---
        self.plotter = QtInteractor(self)
        self.plotter.set_background("white")
        splitter.addWidget(self.plotter.interactor)
        
        splitter.setSizes([250, 300, 700]) # Initial width ratios

        # --- Toolbar ---
        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        
        action_save = toolbar.addAction("Save .cin File")
        action_save.triggered.connect(self.save_input_file)
        
        action_run = toolbar.addAction("Run Solver")
        action_run.triggered.connect(self.run_solver)

        self.show_physics_ui() # Default View

    def on_tree_click(self, item, col):
        """Switch Property View based on Tree Selection."""
        # Clear existing rows
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        text = item.text(0)
        self.props_group.setTitle(f"Properties: {text}")

        if text == "Physics Models":
            self.show_physics_ui()
        elif text == "Material Properties":
            self.show_material_ui()
        elif text == "Initial Conditions":
            self.show_initial_ui()
        elif text == "Numerics & Solvers":
            self.show_numerics_ui()
        elif text == "Time Settings":
            self.show_time_ui()
        elif text == "Run Simulation":
            btn = QPushButton("Start Calculation")
            btn.clicked.connect(self.run_solver)
            self.props_layout.addRow(btn)

    # --- Property UI Generators ---

    def show_physics_ui(self):
        cb_model = QComboBox()
        cb_model.addItems(["Laminar", "k-omega"])
        # Detect current state
        current = "k-omega" if self.case.lcal[4] else "Laminar"
        cb_model.setCurrentText(current)
        cb_model.currentTextChanged.connect(self.update_physics_model)
        self.props_layout.addRow("Turbulence Model:", cb_model)
        
        if current == "k-omega":
            lbl = QLabel("k-omega (Wilcox 1988)")
            lbl.setStyleSheet("color: gray; font-style: italic;")
            self.props_layout.addRow("", lbl)

    def update_physics_model(self, text):
        self.case.set_physics_model(text)

    def show_material_ui(self):
        self.add_double_spin("Density (DENS):", self.case.physics, 'DENS')
        self.add_double_spin("Viscosity (VISC):", self.case.physics, 'VISC', dec=5)
        self.add_double_spin("Prandtl No (PRANL):", self.case.physics, 'PRANL')
        self.add_double_spin("Gravity X:", self.case.physics, 'GRAVX')
        self.add_double_spin("Gravity Y:", self.case.physics, 'GRAVY')
        self.add_double_spin("Thermal Exp (BETA):", self.case.physics, 'BETA')

    def show_initial_ui(self):
        self.add_double_spin("U Velocity (UIN):", self.case.init_fields, 'UIN')
        self.add_double_spin("V Velocity (VIN):", self.case.init_fields, 'VIN')
        self.add_double_spin("Pressure (PIN):", self.case.init_fields, 'PIN')
        self.add_double_spin("Temperature (TIN):", self.case.init_fields, 'TIN')
        self.add_double_spin("Lid Velocity (ULID):", self.case.init_fields, 'ULID')
        
        if self.case.lcal[4]: # If Turbulence is on
            self.add_double_spin("Turb. Kinetic Energy (TEIN):", self.case.init_fields, 'TEIN', dec=5)
            self.add_double_spin("Dissipation (EDIN):", self.case.init_fields, 'EDIN', dec=5)

    def show_numerics_ui(self):
        # Under Relaxation
        self.props_layout.addRow(QLabel("<b>Under-Relaxation Factors (URF)</b>"))
        self.add_list_spin("Velocity (U,V):", self.case.urf, 0)
        self.add_list_spin("Pressure (P):", self.case.urf, 2)
        
        # Schemes
        self.props_layout.addRow(QLabel("<b>Discretization (GDS)</b>"))
        self.props_layout.addRow(QLabel("1.0 = CDS (Central), 0.0 = UDS (Upwind)"))
        self.add_list_spin("Blending Factor U:", self.case.gds, 0)

    def show_time_ui(self):
        chk_steady = QCheckBox("Steady State")
        chk_steady.setChecked(not self.case.logical_control['LTIME'])
        chk_steady.toggled.connect(lambda c: self.case.logical_control.update({'LTIME': not c}))
        self.props_layout.addRow("Mode:", chk_steady)
        
        self.add_int_spin("Time Steps:", self.case.time_control, 'ITSTEP')
        self.add_double_spin("Time Step Size (DT):", self.case.time_control, 'DT', dec=4)

    # --- Helper Widgets ---

    def add_double_spin(self, label, data_dict, key, dec=2):
        sb = QDoubleSpinBox()
        sb.setRange(-1e6, 1e6)
        sb.setDecimals(dec)
        sb.setValue(data_dict[key])
        sb.valueChanged.connect(lambda v: data_dict.update({key: v}))
        self.props_layout.addRow(label, sb)

    def add_int_spin(self, label, data_dict, key):
        sb = QSpinBox()
        sb.setRange(0, 100000)
        sb.setValue(data_dict[key])
        sb.valueChanged.connect(lambda v: data_dict.update({key: v}))
        self.props_layout.addRow(label, sb)

    def add_list_spin(self, label, data_list, index):
        sb = QDoubleSpinBox()
        sb.setRange(0.0, 1.0)
        sb.setSingleStep(0.1)
        sb.setValue(data_list[index])
        sb.valueChanged.connect(lambda v: self._update_list(data_list, index, v))
        self.props_layout.addRow(label, sb)

    def _update_list(self, l, i, v):
        l[i] = v

    # --- Actions ---

    def save_input_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Input File", "", "CAFFA Input (*.cin)")
        if filename:
            try:
                self.case.write_cin_file(filename)
                self.statusBar().showMessage(f"Saved: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def run_solver(self):
        """Mocks the solver run and visualizes results."""
        self.statusBar().showMessage("Running Solver...")
        QApplication.processEvents()
        
        # 1. Simulate getting data
        xx, yy, u, v, p = self.case.run_dummy_simulation()
        
        # 2. PyVista Visualization
        # Create Structured Grid
        grid = pv.StructuredGrid(xx, yy, np.zeros_like(xx))
        grid["Velocity"] = np.column_stack((u.flatten(), v.flatten(), np.zeros(u.size)))
        grid["Pressure"] = p.flatten()
        
        # 3. Plot
        self.plotter.clear()
        self.plotter.add_mesh(grid, scalars="Velocity", cmap="jet", show_edges=False)
        self.plotter.add_axes()
        self.plotter.reset_camera()
        
        # Add Glyphs (Vectors)
        arrows = grid.glyph(orient="Velocity", scale="Velocity", factor=0.1)
        self.plotter.add_mesh(arrows, color="black")
        
        self.statusBar().showMessage("Calculation Finished. Velocity field shown.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CaffaGUI()
    window.show()
    sys.exit(app.exec())