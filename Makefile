# Makefile for Python project

# Variables
SRC = src/
TESTS = tests/
DOCS = docs/

# Run tests using pytest
test:
	@echo "Running tests..."
	pytest $(TESTS) --verbose

# Lint code using pylint
lint:
	@echo "Linting code with pylint..."
	pylint $(SRC) $(TESTS)

# Type checking with mypy
typecheck:
	@echo "Running type checks with mypy..."
	mypy $(SRC)

# Clean up .pyc files and __pycache__ directories
clean:
	@echo "Cleaning up .pyc files and __pycache__ directories..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

# Build documentation with Sphinx
docs:
	@echo "Building Sphinx documentation..."
	$(MAKE) -C $(DOCS) html

# Help command to list all available commands
help:
	@echo "Makefile Commands:"
	@echo "  test       - Run tests with pytest"
	@echo "  lint       - Lint code with pylint"
	@echo "  typecheck  - Run type checking with mypy"
	@echo "  clean      - Clean up .pyc files and __pycache__ directories"
	@echo "  docs       - Build documentation with Sphinx"
	@echo "  help       - Show this help message"

