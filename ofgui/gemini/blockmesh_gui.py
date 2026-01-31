import sys
import os
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, 
                             QVBoxLayout, QWidget, QGroupBox, QFormLayout, 
                             QSpinBox, QDoubleSpinBox, QPushButton, QSplitter, 
                             QFileDialog, QMessageBox, QLabel)
from PyQt6.QtCore import Qt
from pyvistaqt import QtInteractor
import pyvista as pv

class BlockMeshGenerator:
    """Core logic to store block data and write OpenFOAM dict."""
    def __init__(self):
        # Vertices: ID -> [x, y, z]
        self.vertices = {
            0: [0, 0, 0], 1: [1, 0, 0], 2: [1, 1, 0], 3: [0, 1, 0],
            4: [0, 0, 1], 5: [1, 0, 1], 6: [1, 1, 1], 7: [0, 1, 1]
        }
        # Blocks: ID -> [v0, v1, v2, v3, v4, v5, v6, v7] (Hex definition)
        self.blocks = {
            0: {'nodes': [0, 1, 2, 3, 4, 5, 6, 7], 'cells': [20, 20, 20], 'grading': [1, 1, 1]}
        }
        self.edges = {} # Curved edges (structure ready for expansion)
        self.boundaries = {}

    def update_vertex(self, vid, coords):
        self.vertices[vid] = coords

    def get_vtk_grid(self):
        """Generates a UnstructuredGrid for visualization."""
        points = []
        cells = []
        cell_types = []
        
        # Map global vertex ID to local point list index
        v_map = {} 
        current_pt_idx = 0
        
        sorted_vids = sorted(self.vertices.keys())
        for vid in sorted_vids:
            points.append(self.vertices[vid])
            v_map[vid] = current_pt_idx
            current_pt_idx += 1
            
        for bid, data in self.blocks.items():
            # VTK_HEXAHEDRON = 12
            local_ids = [v_map[n] for n in data['nodes']]
            cells.append(8) # Count
            cells.extend(local_ids)
            cell_types.append(12) 
            
        grid = pv.UnstructuredGrid(cells, cell_types, points)
        return grid

    def write_dict(self, filepath):
        with open(filepath, 'w') as f:
            f.write("FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }\n")
            f.write("convertToMeters 1;\n\n")
            
            f.write("vertices (\n")
            for vid in sorted(self.vertices.keys()):
                v = self.vertices[vid]
                f.write(f"    ({v[0]} {v[1]} {v[2]}) // {vid}\n")
            f.write(");\n\n")
            
            f.write("blocks (\n")
            for bid, data in self.blocks.items():
                ns = data['nodes']
                cs = data['cells']
                gs = data['grading']
                # OpenFOAM Hex definition: hex (v0 .. v7) (nx ny nz) simpleGrading (gx gy gz)
                hex_str = " ".join(map(str, ns))
                f.write(f"    hex ({hex_str}) ({cs[0]} {cs[1]} {cs[2]}) simpleGrading ({gs[0]} {gs[1]} {gs[2]})\n")
            f.write(");\n\n")
            
            f.write("edges ();\n")
            f.write("boundary ();\n")
            f.write("mergePatchPairs ();\n")

class ICEMStyleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyBlockMesh (ICEM Style)")
        self.resize(1400, 900)
        
        self.generator = BlockMeshGenerator()
        self.selected_vertex = None
        
        # --- Layout ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)
        
        # LEFT: Model Tree & Properties
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Blocking")
        self.tree.itemClicked.connect(self.on_tree_select)
        left_layout.addWidget(self.tree)
        
        self.props_group = QGroupBox("Properties")
        self.props_layout = QFormLayout()
        self.props_group.setLayout(self.props_layout)
        left_layout.addWidget(self.props_group)
        
        splitter.addWidget(left_panel)
        
        # CENTER: 3D View (ICEM Style Black Background)
        self.plotter = QtInteractor(self)
        self.plotter.set_background("black") 
        self.plotter.add_axes()
        # Enable picking (clicking vertices)
        self.plotter.enable_point_picking(callback=self.on_pick_vertex, show_message=False, color='red', point_size=15, use_picker=True)
        splitter.addWidget(self.plotter.interactor)
        
        splitter.setSizes([300, 1100])
        
        # --- Toolbar ---
        toolbar = self.addToolBar("Main")
        toolbar.addAction("Export blockMeshDict").triggered.connect(self.export_dict)
        toolbar.addAction("Reset View").triggered.connect(self.reset_view)
        
        # --- Init ---
        self.refresh_tree()
        self.refresh_view()
        
    def refresh_tree(self):
        self.tree.clear()
        root = QTreeWidgetItem(self.tree, ["Geometry"])
        
        # Blocks Node
        blk_node = QTreeWidgetItem(root, ["Blocks"])
        for bid in self.generator.blocks:
            item = QTreeWidgetItem(blk_node, [f"Block {bid}"])
            item.setData(0, Qt.ItemDataRole.UserRole, ('block', bid))
            
        # Vertices Node
        vtx_node = QTreeWidgetItem(root, ["Vertices"])
        for vid, coords in self.generator.vertices.items():
            item = QTreeWidgetItem(vtx_node, [f"Vertex {vid}"])
            item.setData(0, Qt.ItemDataRole.UserRole, ('vertex', vid))
            
        root.setExpanded(True)
        blk_node.setExpanded(True)
        vtx_node.setExpanded(True)

    def refresh_view(self):
        self.plotter.clear()
        
        # Get Grid
        grid = self.generator.get_vtk_grid()
        
        # Draw Wireframe (Blocking structure - Cyan color is classic ICEM)
        self.plotter.add_mesh(grid, style='wireframe', color='cyan', line_width=3, label="Blocking")
        
        # Draw Points (Vertices - Yellow Spheres)
        pts = np.array([self.generator.vertices[i] for i in sorted(self.generator.vertices.keys())])
        self.plotter.add_points(pts, color='yellow', point_size=10, render_points_as_spheres=True)
        
        # Add labels (Vertex IDs)
        self.plotter.add_point_labels(pts, [str(i) for i in sorted(self.generator.vertices.keys())], 
                                      font_size=14, text_color='white', always_visible=True)
        
        # Note: Camera is not reset here to allow user zoom persistence during edits

    def on_tree_select(self, item, col):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data: return
        
        type_, id_ = data
        self.clear_props()
        
        if type_ == 'vertex':
            self.selected_vertex = id_
            self.show_vertex_props(id_)
        elif type_ == 'block':
            self.show_block_props(id_)

    def on_pick_vertex(self, mesh, idx):
        """Callback when a user clicks a vertex in 3D view."""
        # Note: idx matches the sorted order of vertices passed to add_points
        if idx is not None:
             self.selected_vertex = idx
             self.clear_props()
             self.show_vertex_props(idx)

    # --- Property Editors ---

    def clear_props(self):
        while self.props_layout.count():
            child = self.props_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

    def show_vertex_props(self, vid):
        if vid not in self.generator.vertices: return
        coords = self.generator.vertices[vid]
        
        self.props_layout.addRow(QLabel(f"<b>Vertex {vid}</b>"))
        
        self.sb_x = self.create_coord_spin(coords[0])
        self.sb_y = self.create_coord_spin(coords[1])
        self.sb_z = self.create_coord_spin(coords[2])
        
        self.props_layout.addRow("X:", self.sb_x)
        self.props_layout.addRow("Y:", self.sb_y)
        self.props_layout.addRow("Z:", self.sb_z)
        
        btn = QPushButton("Move Vertex")
        btn.clicked.connect(lambda: self.update_vertex_pos(vid))
        self.props_layout.addRow(btn)

    def create_coord_spin(self, val):
        sb = QDoubleSpinBox()
        sb.setRange(-10000, 10000)
        sb.setSingleStep(0.1)
        sb.setValue(val)
        return sb

    def update_vertex_pos(self, vid):
        new_pos = [self.sb_x.value(), self.sb_y.value(), self.sb_z.value()]
        self.generator.update_vertex(vid, new_pos)
        self.refresh_view() # Redraw scene with new geometry

    def show_block_props(self, bid):
        data = self.generator.blocks[bid]
        self.props_layout.addRow(QLabel(f"<b>Block {bid}</b>"))
        
        # Mesh Parameters
        self.sb_nx = QSpinBox()
        self.sb_nx.setValue(data['cells'][0])
        self.sb_ny = QSpinBox()
        self.sb_ny.setValue(data['cells'][1])
        self.sb_nz = QSpinBox()
        self.sb_nz.setValue(data['cells'][2])
        
        self.props_layout.addRow("Cells X:", self.sb_nx)
        self.props_layout.addRow("Cells Y:", self.sb_ny)
        self.props_layout.addRow("Cells Z:", self.sb_nz)
        
        btn = QPushButton("Update Mesh Params")
        btn.clicked.connect(lambda: self.update_block_params(bid))
        self.props_layout.addRow(btn)

    def update_block_params(self, bid):
        self.generator.blocks[bid]['cells'] = [
            self.sb_nx.value(), self.sb_ny.value(), self.sb_nz.value()
        ]
        QMessageBox.information(self, "Updated", f"Block {bid} mesh parameters updated.")

    def export_dict(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save blockMeshDict", "blockMeshDict", "Dict (*)")
        if fname:
            self.generator.write_dict(fname)
            QMessageBox.information(self, "Success", f"Written to {fname}")

    def reset_view(self):
        self.plotter.reset_camera()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ICEMStyleGUI()
    window.show()
    sys.exit(app.exec())