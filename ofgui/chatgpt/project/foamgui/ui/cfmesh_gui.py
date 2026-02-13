from PyQt6.QtWidgets import QWidget, QFormLayout, QDoubleSpinBox

class CfMeshGUI(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        box = QDoubleSpinBox()
        box.setValue(0.02)
        layout.addRow('Max Cell Size', box)
