from PyQt6.QtWidgets import QApplication
import sys
from foamgui.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
