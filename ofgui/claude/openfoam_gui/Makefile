# OpenFOAM GUI Makefile

.PHONY: help install test clean docker

help:
	@echo "OpenFOAM GUI - Development Commands"
	@echo ""
	@echo "  install     - Install application and dependencies"
	@echo "  test        - Run all tests"
	@echo "  test-unit   - Run unit tests only"
	@echo "  test-gui    - Run GUI automation tests"
	@echo "  test-perf   - Run performance tests"
	@echo "  clean       - Remove build artifacts"
	@echo "  docker      - Build Docker image"
	@echo "  format      - Format code with black"
	@echo "  lint        - Run linters"
	@echo "  docs        - Generate documentation"

install:
	bash install.sh

test:
	./run_tests.sh

test-unit:
	PYTHONPATH=src python tests/unit/test_core.py

test-gui:
	PYTHONPATH=src pytest tests/gui/test_gui_automation.py -v

test-perf:
	PYTHONPATH=src python tests/performance/test_performance.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/

docker:
	docker-compose build

format:
	black src/ tests/

lint:
	flake8 src/ tests/
	mypy src/

docs:
	@echo "Documentation is in docs/"
	@echo "Main docs: README.md"
