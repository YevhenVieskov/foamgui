from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox

class SnappyHexMeshGUI(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QCheckBox('Castellated'))
        layout.addWidget(QCheckBox('Snap'))
        layout.addWidget(QCheckBox('Layers'))
