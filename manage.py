# manage.py

import os
import subprocess
import argparse

def run_tests():
    """Run tests using pytest."""
    print("Running tests...")
    result = subprocess.run(['pytest', '--verbose'], check=False)
    return result.returncode

def lint_code():
    """Lint code using pylint."""
    print("Linting code with pylint...")
    result = subprocess.run(['pylint', 'src', 'tests'], check=False)
    return result.returncode

def clean():
    """Remove .pyc files and __pycache__ directories."""
    print("Cleaning up .pyc files and __pycache__ directories...")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                os.remove(os.path.join(root, file))
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            for item in os.listdir(pycache_path):
                os.remove(os.path.join(pycache_path, item))
            os.rmdir(pycache_path)
    print("Cleanup complete.")

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Manage.py - Manage common tasks")
    parser.add_argument("command", choices=["test", "lint", "clean"], help="Command to run")
    return parser.parse_args()

def type_check():
    """Run mypy for type checking."""
    print("Running mypy type check...")
    result = subprocess.run(['mypy', 'src/'], check=False)
    return result.returncode

def build_docs():
    """Build Sphinx documentation."""
    print("Building Sphinx documentation...")
    result = subprocess.run(['sphinx-build', '-b', 'html', 'docs/source', 'docs/build/html'], check=False)
    return result.returncode


def main():
    """Main entry point for the script."""
    args = parse_args()

    if args.command == "test":
        exit_code = run_tests()
    elif args.command == "lint":
        exit_code = lint_code()
    elif args.command == "clean":
        clean()
        exit_code = 0
    else:
        print(f"Unknown command: {args.command}")
        exit_code = 1

    exit(exit_code)

if __name__ == "__main__":
    main()
