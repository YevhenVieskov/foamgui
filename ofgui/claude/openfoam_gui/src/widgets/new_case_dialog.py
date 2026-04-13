"""New case creation dialog"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                              QPushButton, QFileDialog, QComboBox, QDialogButtonBox)
from pathlib import Path


class NewCaseDialog(QDialog):
    """Dialog for creating new OpenFOAM case"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New OpenFOAM Case")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Case Name:", self.name_edit)
        
        self.path_edit = QLineEdit(str(Path.home()))
        path_btn = QPushButton("Browse...")
        path_btn.clicked.connect(self._browse_path)
        path_layout = QVBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(path_btn)
        form.addRow("Location:", path_layout)
        
        self.solver_combo = QComboBox()
        self.solver_combo.addItems(['simpleFoam', 'pimpleFoam', 'icoFoam', 'interFoam', 'buoyantSimpleFoam'])
        form.addRow("Solver:", self.solver_combo)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _browse_path(self):
        """Browse for case location"""
        path = QFileDialog.getExistingDirectory(self, "Select Location", str(Path.home()))
        if path:
            self.path_edit.setText(path)
    
    def get_case_data(self) -> dict:
        """Get case data from dialog"""
        return {
            'name': self.name_edit.text(),
            'path': self.path_edit.text(),
            'solver': self.solver_combo.currentText(),
            'dimension': '3D'
        }
