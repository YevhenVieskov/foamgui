"""
Visual blockMesh editor - ICEM CFD style
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QTableWidget,
    QTableWidgetItem, QSplitter, QGroupBox, QFormLayout, QToolBar,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
import pyvista as pv
from pyvistaqt import QtInteractor
import numpy as np
from pathlib import Path
import json


class BlockMeshEditorWidget(QMainWindow):
    """Visual blockMesh editor with 3D preview"""
    
    def __init__(self, case_path: str, config):
        super().__init__()
        self.case_path = Path(case_path)
        self.config = config
        self.blocks = []
        self.vertices = []
        self.edges = []
        self.boundaries = []
        self.selected_block = None
        
        self.setWindowTitle(f"blockMesh Editor - {self.case_path.name}")
        self.setGeometry(100, 100, 1400, 800)
        
        self._create_ui()
        self._load_existing_blockmesh()
    
    def _create_ui(self):
        """Create user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Create toolbar
        self._create_toolbar()
        
        # Left panel - controls
        left_panel = self._create_control_panel()
        main_layout.addWidget(left_panel, stretch=1)
        
        # Right panel - 3D viewer
        right_panel = self._create_viewer_panel()
        main_layout.addWidget(right_panel, stretch=3)
    
    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        new_action = QAction("New Block", self)
        new_action.triggered.connect(self._add_block)
        toolbar.addAction(new_action)
        
        delete_action = QAction("Delete Block", self)
        delete_action.triggered.connect(self._delete_block)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        save_action = QAction("Save blockMeshDict", self)
        save_action.triggered.connect(self._save_blockmesh)
        toolbar.addAction(save_action)
        
        generate_action = QAction("Generate Mesh", self)
        generate_action.triggered.connect(self._generate_mesh)
        toolbar.addAction(generate_action)
    
    def _create_control_panel(self) -> QWidget:
        """Create control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Vertices group
        vertices_group = QGroupBox("Vertices")
        vertices_layout = QVBoxLayout()
        
        self.vertices_table = QTableWidget()
        self.vertices_table.setColumnCount(4)
        self.vertices_table.setHorizontalHeaderLabels(['ID', 'X', 'Y', 'Z'])
        self.vertices_table.cellChanged.connect(self._on_vertex_changed)
        vertices_layout.addWidget(self.vertices_table)
        
        vertices_buttons = QHBoxLayout()
        add_vertex_btn = QPushButton("Add Vertex")
        add_vertex_btn.clicked.connect(self._add_vertex)
        remove_vertex_btn = QPushButton("Remove Vertex")
        remove_vertex_btn.clicked.connect(self._remove_vertex)
        vertices_buttons.addWidget(add_vertex_btn)
        vertices_buttons.addWidget(remove_vertex_btn)
        vertices_layout.addLayout(vertices_buttons)
        
        vertices_group.setLayout(vertices_layout)
        layout.addWidget(vertices_group)
        
        # Blocks group
        blocks_group = QGroupBox("Blocks")
        blocks_layout = QVBoxLayout()
        
        self.blocks_table = QTableWidget()
        self.blocks_table.setColumnCount(4)
        self.blocks_table.setHorizontalHeaderLabels(['ID', 'Vertices', 'Cells', 'Grading'])
        self.blocks_table.itemSelectionChanged.connect(self._on_block_selected)
        blocks_layout.addWidget(self.blocks_table)
        
        # Block details
        block_details = QFormLayout()
        
        self.cells_x = QSpinBox()
        self.cells_x.setRange(1, 1000)
        self.cells_x.setValue(10)
        self.cells_x.valueChanged.connect(self._update_selected_block)
        
        self.cells_y = QSpinBox()
        self.cells_y.setRange(1, 1000)
        self.cells_y.setValue(10)
        self.cells_y.valueChanged.connect(self._update_selected_block)
        
        self.cells_z = QSpinBox()
        self.cells_z.setRange(1, 1000)
        self.cells_z.setValue(10)
        self.cells_z.valueChanged.connect(self._update_selected_block)
        
        self.grading_x = QDoubleSpinBox()
        self.grading_x.setRange(0.01, 100)
        self.grading_x.setValue(1.0)
        self.grading_x.setDecimals(3)
        self.grading_x.valueChanged.connect(self._update_selected_block)
        
        self.grading_y = QDoubleSpinBox()
        self.grading_y.setRange(0.01, 100)
        self.grading_y.setValue(1.0)
        self.grading_y.setDecimals(3)
        self.grading_y.valueChanged.connect(self._update_selected_block)
        
        self.grading_z = QDoubleSpinBox()
        self.grading_z.setRange(0.01, 100)
        self.grading_z.setValue(1.0)
        self.grading_z.setDecimals(3)
        self.grading_z.valueChanged.connect(self._update_selected_block)
        
        block_details.addRow("Cells X:", self.cells_x)
        block_details.addRow("Cells Y:", self.cells_y)
        block_details.addRow("Cells Z:", self.cells_z)
        block_details.addRow("Grading X:", self.grading_x)
        block_details.addRow("Grading Y:", self.grading_y)
        block_details.addRow("Grading Z:", self.grading_z)
        
        blocks_layout.addLayout(block_details)
        blocks_group.setLayout(blocks_layout)
        layout.addWidget(blocks_group)
        
        # Boundaries group
        boundaries_group = QGroupBox("Boundaries")
        boundaries_layout = QVBoxLayout()
        
        self.boundaries_table = QTableWidget()
        self.boundaries_table.setColumnCount(3)
        self.boundaries_table.setHorizontalHeaderLabels(['Name', 'Type', 'Faces'])
        boundaries_layout.addWidget(self.boundaries_table)
        
        boundaries_buttons = QHBoxLayout()
        add_boundary_btn = QPushButton("Add Boundary")
        add_boundary_btn.clicked.connect(self._add_boundary)
        remove_boundary_btn = QPushButton("Remove Boundary")
        remove_boundary_btn.clicked.connect(self._remove_boundary)
        boundaries_buttons.addWidget(add_boundary_btn)
        boundaries_buttons.addWidget(remove_boundary_btn)
        boundaries_layout.addLayout(boundaries_buttons)
        
        boundaries_group.setLayout(boundaries_layout)
        layout.addWidget(boundaries_group)
        
        layout.addStretch()
        return panel
    
    def _create_viewer_panel(self) -> QWidget:
        """Create 3D viewer panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # PyVista viewer
        self.plotter = QtInteractor(panel)
        layout.addWidget(self.plotter.interactor)
        
        # View controls
        controls = QHBoxLayout()
        
        view_xy_btn = QPushButton("View XY")
        view_xy_btn.clicked.connect(lambda: self.plotter.view_xy())
        
        view_xz_btn = QPushButton("View XZ")
        view_xz_btn.clicked.connect(lambda: self.plotter.view_xz())
        
        view_yz_btn = QPushButton("View YZ")
        view_yz_btn.clicked.connect(lambda: self.plotter.view_yz())
        
        reset_btn = QPushButton("Reset View")
        reset_btn.clicked.connect(lambda: self.plotter.reset_camera())
        
        controls.addWidget(view_xy_btn)
        controls.addWidget(view_xz_btn)
        controls.addWidget(view_yz_btn)
        controls.addWidget(reset_btn)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        return panel
    
    def _add_vertex(self):
        """Add new vertex"""
        row = self.vertices_table.rowCount()
        self.vertices_table.insertRow(row)
        
        vertex = [0.0, 0.0, 0.0]
        self.vertices.append(vertex)
        
        self.vertices_table.setItem(row, 0, QTableWidgetItem(str(row)))
        for col in range(3):
            self.vertices_table.setItem(row, col + 1, QTableWidgetItem(str(vertex[col])))
        
        self._update_viewer()
    
    def _remove_vertex(self):
        """Remove selected vertex"""
        current_row = self.vertices_table.currentRow()
        if current_row >= 0:
            self.vertices_table.removeRow(current_row)
            self.vertices.pop(current_row)
            self._update_vertex_ids()
            self._update_viewer()
    
    def _on_vertex_changed(self, row: int, col: int):
        """Handle vertex value change"""
        if col > 0:  # Skip ID column
            try:
                value = float(self.vertices_table.item(row, col).text())
                self.vertices[row][col - 1] = value
                self._update_viewer()
            except (ValueError, IndexError):
                pass
    
    def _update_vertex_ids(self):
        """Update vertex IDs after deletion"""
        for row in range(self.vertices_table.rowCount()):
            self.vertices_table.setItem(row, 0, QTableWidgetItem(str(row)))
    
    def _add_block(self):
        """Add new block"""
        if len(self.vertices) < 8:
            QMessageBox.warning(self, "Warning", "Need at least 8 vertices to create a block")
            return
        
        # Create block from first 8 vertices
        block = {
            'vertices': list(range(min(8, len(self.vertices)))),
            'cells': [self.cells_x.value(), self.cells_y.value(), self.cells_z.value()],
            'grading': [self.grading_x.value(), self.grading_y.value(), self.grading_z.value()]
        }
        self.blocks.append(block)
        
        row = self.blocks_table.rowCount()
        self.blocks_table.insertRow(row)
        
        self.blocks_table.setItem(row, 0, QTableWidgetItem(str(row)))
        self.blocks_table.setItem(row, 1, QTableWidgetItem(str(block['vertices'])))
        self.blocks_table.setItem(row, 2, QTableWidgetItem(str(block['cells'])))
        self.blocks_table.setItem(row, 3, QTableWidgetItem(str(block['grading'])))
        
        self._update_viewer()
    
    def _delete_block(self):
        """Delete selected block"""
        current_row = self.blocks_table.currentRow()
        if current_row >= 0:
            self.blocks_table.removeRow(current_row)
            self.blocks.pop(current_row)
            self._update_viewer()
    
    def _on_block_selected(self):
        """Handle block selection"""
        current_row = self.blocks_table.currentRow()
        if current_row >= 0:
            self.selected_block = current_row
            block = self.blocks[current_row]
            
            self.cells_x.setValue(block['cells'][0])
            self.cells_y.setValue(block['cells'][1])
            self.cells_z.setValue(block['cells'][2])
            
            self.grading_x.setValue(block['grading'][0])
            self.grading_y.setValue(block['grading'][1])
            self.grading_z.setValue(block['grading'][2])
    
    def _update_selected_block(self):
        """Update selected block parameters"""
        if self.selected_block is not None and self.selected_block < len(self.blocks):
            block = self.blocks[self.selected_block]
            block['cells'] = [self.cells_x.value(), self.cells_y.value(), self.cells_z.value()]
            block['grading'] = [self.grading_x.value(), self.grading_y.value(), self.grading_z.value()]
            
            row = self.selected_block
            self.blocks_table.setItem(row, 2, QTableWidgetItem(str(block['cells'])))
            self.blocks_table.setItem(row, 3, QTableWidgetItem(str(block['grading'])))
    
    def _add_boundary(self):
        """Add boundary patch"""
        row = self.boundaries_table.rowCount()
        self.boundaries_table.insertRow(row)
        
        self.boundaries_table.setItem(row, 0, QTableWidgetItem(f"patch{row}"))
        self.boundaries_table.setItem(row, 1, QTableWidgetItem("patch"))
        self.boundaries_table.setItem(row, 2, QTableWidgetItem("()"))
    
    def _remove_boundary(self):
        """Remove boundary patch"""
        current_row = self.boundaries_table.currentRow()
        if current_row >= 0:
            self.boundaries_table.removeRow(current_row)
    
    def _update_viewer(self):
        """Update 3D visualization"""
        self.plotter.clear()
        
        # Plot vertices
        if self.vertices:
            vertices_array = np.array(self.vertices)
            self.plotter.add_points(vertices_array, color='red', point_size=10, render_points_as_spheres=True)
            
            # Add vertex labels
            for i, vertex in enumerate(self.vertices):
                self.plotter.add_point_labels([vertex], [str(i)], font_size=12, point_color='red', text_color='white')
        
        # Plot blocks
        for i, block in enumerate(self.blocks):
            if len(block['vertices']) == 8:
                v_indices = block['vertices']
                if all(idx < len(self.vertices) for idx in v_indices):
                    # Create hexahedron
                    points = np.array([self.vertices[idx] for idx in v_indices])
                    
                    # Define hexahedron faces
                    faces = np.array([
                        [4, 0, 1, 2, 3],  # bottom
                        [4, 4, 5, 6, 7],  # top
                        [4, 0, 1, 5, 4],  # front
                        [4, 2, 3, 7, 6],  # back
                        [4, 0, 3, 7, 4],  # left
                        [4, 1, 2, 6, 5],  # right
                    ])
                    
                    mesh = pv.PolyData(points, faces)
                    self.plotter.add_mesh(mesh, color='lightblue', opacity=0.3, show_edges=True, line_width=2)
                    
                    # Add block label
                    center = points.mean(axis=0)
                    self.plotter.add_point_labels([center], [f"Block {i}"], font_size=14, text_color='blue')
        
        # Add axes
        self.plotter.add_axes()
        self.plotter.reset_camera()
    
    def _save_blockmesh(self):
        """Save blockMeshDict file"""
        try:
            blockmesh_dict = self._generate_blockmesh_dict()
            
            system_dir = self.case_path / 'system'
            system_dir.mkdir(exist_ok=True)
            
            with open(system_dir / 'blockMeshDict', 'w') as f:
                f.write(blockmesh_dict)
            
            QMessageBox.information(self, "Success", "blockMeshDict saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save blockMeshDict: {e}")
    
    def _generate_blockmesh_dict(self) -> str:
        """Generate blockMeshDict content"""
        # Vertices
        vertices_str = "(\n"
        for vertex in self.vertices:
            vertices_str += f"    ({vertex[0]} {vertex[1]} {vertex[2]})\n"
        vertices_str += ")"
        
        # Blocks
        blocks_str = "(\n"
        for block in self.blocks:
            v = block['vertices']
            cells = block['cells']
            grading = block['grading']
            blocks_str += f"    hex ({' '.join(map(str, v))}) ({cells[0]} {cells[1]} {cells[2]}) simpleGrading ({grading[0]} {grading[1]} {grading[2]})\n"
        blocks_str += ")"
        
        # Boundaries
        boundaries_str = "(\n"
        for row in range(self.boundaries_table.rowCount()):
            name = self.boundaries_table.item(row, 0).text()
            btype = self.boundaries_table.item(row, 1).text()
            faces = self.boundaries_table.item(row, 2).text()
            boundaries_str += f"    {name}\n    {{\n        type {btype};\n        faces\n        {faces};\n    }}\n"
        boundaries_str += ")"
        
        blockmesh_dict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

convertToMeters 1;

vertices
{vertices_str};

blocks
{blocks_str};

edges
(
);

boundary
{boundaries_str};

mergePatchPairs
(
);

// ************************************************************************* //
"""
        return blockmesh_dict
    
    def _generate_mesh(self):
        """Generate mesh using blockMesh"""
        self._save_blockmesh()
        
        from core.case_manager import CaseManager
        case_manager = CaseManager(self.config)
        
        try:
            case_manager.run_mesher(str(self.case_path), 'blockMesh')
            QMessageBox.information(self, "Success", "Mesh generated successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate mesh: {e}")
    
    def _load_existing_blockmesh(self):
        """Load existing blockMeshDict if available"""
        blockmesh_file = self.case_path / 'system' / 'blockMeshDict'
        if blockmesh_file.exists():
            # TODO: Parse existing blockMeshDict
            # This would require a proper OpenFOAM dictionary parser
            pass
