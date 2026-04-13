#!/usr/bin/env python3
"""
OpenFOAM GUI - Star-CCM+ like interface for OpenFOAM
Main application entry point
"""
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from core.main_window import MainWindow
from core.config import AppConfig


def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("OpenFOAM GUI")
    app.setOrganizationName("OpenFOAM")
    app.setApplicationVersion("1.0.0")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Load configuration
    config = AppConfig()
    
    # Create and show main window
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
