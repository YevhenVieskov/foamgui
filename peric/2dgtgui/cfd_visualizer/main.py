#!/usr/bin/env python3
"""
Star CCM+ Like CFD Visualization GUI
Main entry point for the application
"""

import sys
from qtpy.QtWidgets import QApplication
from gui.main_window import CFDMainWindow
from gui.data_loader import CFDDataLoader

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("CFD Visualizer")
    app.setOrganizationName("CFD Tools")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = CFDMainWindow()
    window.show()
    
    # Load sample data if available
    loader = CFDDataLoader()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
CAFFA Visualizer - Star CCM+ Style
Main entry point for the application
"""

import sys
from qtpy.QtWidgets import QApplication
from gui.main_window import CFDMainWindow

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("CAFFA Visualizer")
    app.setOrganizationName("CFD Tools")
    app.setApplicationVersion("1.0.0")
    
    # Set application style (Star CCM+ like)
    app.setStyle('Fusion')
    
    # Set palette
    from qtpy.QtGui import QPalette, QColor
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Create and show main window
    window = CFDMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()