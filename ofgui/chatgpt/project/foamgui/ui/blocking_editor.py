from PyQt6.QtWidgets import QWidget, QVBoxLayout
from pyvistaqt import QtInteractor

class BlockingEditor(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.viewer = QtInteractor(self)
        layout.addWidget(self.viewer)
