from PyQt6.QtWidgets import QMainWindow, QTabWidget
from foamgui.ui.blocking_editor import BlockingEditor
from foamgui.ui.snappy_gui import SnappyHexMeshGUI
from foamgui.ui.cfmesh_gui import CfMeshGUI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FoamGUI')
        tabs = QTabWidget()
        tabs.addTab(BlockingEditor(), 'Blocking')
        tabs.addTab(SnappyHexMeshGUI(), 'snappyHexMesh')
        tabs.addTab(CfMeshGUI(), 'cfMesh')
        self.setCentralWidget(tabs)
