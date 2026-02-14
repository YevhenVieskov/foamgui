#!/bin/bash
# OpenFOAM GUI Universal Installer
# Supports Ubuntu, Debian, Fedora, macOS, and Windows (WSL)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.openfoam_gui}"
VENV_DIR="$INSTALL_DIR/venv"
LOG_FILE="$INSTALL_DIR/install.log"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║          OpenFOAM GUI Installer v1.0                         ║"
    echo "║          Star-CCM+ Style Interface for OpenFOAM              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_step() {
    echo -e "${BLUE}➜ $1${NC}"
}

detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
            VER=$VERSION_ID
        else
            OS="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    
    echo "$OS"
}

check_python() {
    print_step "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -ge 8 ]; then
            print_success "Python $PYTHON_VERSION found"
            PYTHON_CMD="python3"
            return 0
        else
            print_error "Python 3.8+ required (found $PYTHON_VERSION)"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

install_system_dependencies() {
    print_step "Installing system dependencies..."
    
    OS=$(detect_os)
    
    case $OS in
        ubuntu|debian)
            print_info "Detected Debian/Ubuntu system"
            sudo apt-get update
            sudo apt-get install -y \
                python3-pip \
                python3-venv \
                python3-dev \
                libgl1-mesa-dev \
                libgl1-mesa-glx \
                qt6-base-dev \
                build-essential \
                git
            ;;
        
        fedora|rhel|centos)
            print_info "Detected Fedora/RHEL system"
            sudo dnf install -y \
                python3-pip \
                python3-devel \
                mesa-libGL-devel \
                qt6-qtbase-devel \
                gcc \
                gcc-c++ \
                git
            ;;
        
        macos)
            print_info "Detected macOS system"
            if ! command -v brew &> /dev/null; then
                print_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew install python@3.11 qt6
            ;;
        
        *)
            print_error "Unsupported OS: $OS"
            print_info "Please install dependencies manually"
            return 1
            ;;
    esac
    
    print_success "System dependencies installed"
}

create_virtual_environment() {
    print_step "Creating virtual environment..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    
    # Create virtual environment
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    print_success "Virtual environment created at $VENV_DIR"
}

install_python_packages() {
    print_step "Installing Python packages..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install from requirements.txt
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        pip install -r "$SCRIPT_DIR/requirements.txt"
    else
        # Install packages directly
        pip install \
            PyQt6 \
            pyvista \
            pyvistaqt \
            vtk \
            numpy \
            matplotlib \
            scipy \
            psutil
    fi
    
    print_success "Python packages installed"
}

install_application() {
    print_step "Installing OpenFOAM GUI..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install in development mode
    cd "$SCRIPT_DIR"
    pip install -e .
    
    print_success "OpenFOAM GUI installed"
}

create_launcher_script() {
    print_step "Creating launcher script..."
    
    LAUNCHER="$INSTALL_DIR/openfoam-gui"
    
    cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
# OpenFOAM GUI Launcher

INSTALL_DIR="$(dirname "$(readlink -f "$0")")"
VENV_DIR="$INSTALL_DIR/venv"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Launch application
cd "$INSTALL_DIR"
python -m main "$@"
EOF
    
    chmod +x "$LAUNCHER"
    
    print_success "Launcher created at $LAUNCHER"
}

create_desktop_entry() {
    print_step "Creating desktop entry..."
    
    if [ "$OS" == "macos" ]; then
        print_info "Desktop entry not needed on macOS"
        return 0
    fi
    
    DESKTOP_FILE="$HOME/.local/share/applications/openfoam-gui.desktop"
    mkdir -p "$(dirname "$DESKTOP_FILE")"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=OpenFOAM GUI
Comment=Star-CCM+ style interface for OpenFOAM
Exec=$INSTALL_DIR/openfoam-gui
Icon=$SCRIPT_DIR/resources/icons/app-icon.png
Terminal=false
Categories=Science;Engineering;
EOF
    
    chmod +x "$DESKTOP_FILE"
    
    print_success "Desktop entry created"
}

add_to_path() {
    print_step "Adding to PATH..."
    
    # Determine shell config file
    if [ -n "$BASH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    else
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    # Add to PATH if not already present
    if ! grep -q "OPENFOAM_GUI" "$SHELL_CONFIG"; then
        echo "" >> "$SHELL_CONFIG"
        echo "# OpenFOAM GUI" >> "$SHELL_CONFIG"
        echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_CONFIG"
        
        print_success "Added to PATH in $SHELL_CONFIG"
        print_info "Run 'source $SHELL_CONFIG' or restart terminal to use 'openfoam-gui' command"
    else
        print_info "Already in PATH"
    fi
}

verify_installation() {
    print_step "Verifying installation..."
    
    source "$VENV_DIR/bin/activate"
    
    # Test imports
    python3 << 'EOF'
import sys
try:
    import PyQt6
    import pyvista
    import vtk
    import numpy
    import matplotlib
    print("All dependencies OK")
    sys.exit(0)
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Installation verified"
        return 0
    else
        print_error "Verification failed"
        return 1
    fi
}

run_tests() {
    print_step "Running tests..."
    
    source "$VENV_DIR/bin/activate"
    cd "$SCRIPT_DIR"
    
    # Run unit tests
    PYTHONPATH=src python tests/unit/test_core.py
    
    if [ $? -eq 0 ]; then
        print_success "Tests passed"
    else
        print_error "Some tests failed"
    fi
}

print_summary() {
    echo ""
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║          Installation Complete!                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo "Installation directory: $INSTALL_DIR"
    echo "Virtual environment:    $VENV_DIR"
    echo ""
    echo "To run OpenFOAM GUI:"
    echo "  1. $INSTALL_DIR/openfoam-gui"
    echo "  2. Or add to PATH and run: openfoam-gui"
    echo ""
    echo "To activate virtual environment:"
    echo "  source $VENV_DIR/bin/activate"
    echo ""
    echo "To run tests:"
    echo "  cd $SCRIPT_DIR && ./run_tests.sh"
    echo ""
    echo "Documentation:"
    echo "  README.md         - User guide"
    echo "  INSTALL.md        - Installation details"
    echo "  docs/             - Additional documentation"
    echo ""
    echo -e "${YELLOW}Note: Make sure OpenFOAM is installed and sourced${NC}"
    echo ""
}

# Main installation flow
main() {
    print_header
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    {
        # Installation steps
        check_python || exit 1
        
        echo ""
        read -p "Install system dependencies? (requires sudo) [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_system_dependencies
        else
            print_info "Skipping system dependencies"
        fi
        
        echo ""
        create_virtual_environment
        install_python_packages
        install_application
        create_launcher_script
        
        # Optional steps
        echo ""
        read -p "Create desktop entry? [Y/n]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            create_desktop_entry
        fi
        
        echo ""
        read -p "Add to PATH? [Y/n]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            add_to_path
        fi
        
        echo ""
        verify_installation
        
        echo ""
        read -p "Run tests? [y/N]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            run_tests
        fi
        
        echo ""
        print_summary
        
    } 2>&1 | tee "$LOG_FILE"
}

# Run main function
main "$@"
