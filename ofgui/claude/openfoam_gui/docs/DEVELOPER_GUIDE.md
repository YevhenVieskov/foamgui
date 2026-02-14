# Developer Guide

## Development Setup

### Environment Setup

```bash
# Clone repository
git clone https://github.com/yourusername/openfoam-gui.git
cd openfoam-gui

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### IDE Configuration

#### VS Code
- Enable flake8 linting
- Set black as formatter
- Configure pytest

#### PyCharm
- Add virtual environment interpreter
- Set pytest as default test runner

## Architecture Overview

### Core Components

- **AppConfig**: Application configuration management
- **CaseManager**: OpenFOAM case operations
- **SolverRegistry**: Solver metadata and validation
- **Widgets**: UI components for different functionalities

### Design Principles

1. Separation of concerns
2. Model-View-Controller pattern
3. Modularity and reusability
4. Comprehensive testing
5. Extensible architecture

## Adding New Features

See full documentation in the DEVELOPER_GUIDE.md file.

## Testing

```bash
# Run all tests
./run_tests.sh

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Contributing

1. Fork repository
2. Create feature branch
3. Write tests
4. Submit pull request

See CONTRIBUTING.md for details.
