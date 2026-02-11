#!/bin/bash
# CAFFA GUI Installation Script

echo "============================================"
echo "CAFFA CFD Visualization GUI"
echo "Installation Script"
echo "============================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is required but not found."
    echo "Please install Python 3.7 or later."
    exit 1
fi

echo ""
echo "Select installation option:"
echo "1) Full installation (PyQt5 + PyVista + VTK)"
echo "2) Lightweight (Matplotlib only)"
echo "3) Development (includes testing tools)"
echo ""
read -p "Enter option (1-3): " option

case $option in
    1)
        echo ""
        echo "Installing full dependencies..."
        pip install --break-system-packages PyQt5 pyvista vtk numpy scipy matplotlib
        echo ""
        echo "Installation complete!"
        echo "Run the GUI with: python caffa_gui.py"
        ;;
    2)
        echo ""
        echo "Installing lightweight dependencies..."
        pip install --break-system-packages numpy matplotlib
        echo ""
        echo "Installation complete!"
        echo "Run the viewer with: python caffa_viewer_matplotlib.py"
        ;;
    3)
        echo ""
        echo "Installing development dependencies..."
        pip install --break-system-packages PyQt5 pyvista vtk numpy scipy matplotlib pytest pytest-qt
        echo ""
        echo "Installation complete!"
        echo "Run tests with:"
        echo "  python test_caffa_reader.py"
        echo "  python test_functional.py"
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac

echo ""
echo "============================================"
echo "Next Steps:"
echo "============================================"
echo ""
echo "1. Try the examples:"
echo "   python examples_usage.py"
echo ""
echo "2. Run the tests:"
echo "   python test_caffa_reader.py"
echo ""
echo "3. Launch the GUI:"
echo "   python caffa_gui.py              # Full GUI"
echo "   python caffa_viewer_matplotlib.py # Matplotlib"
echo ""
echo "4. Read the documentation:"
echo "   cat README_FINAL.md"
echo ""
echo "============================================"
echo "Installation complete!"
echo "============================================"
