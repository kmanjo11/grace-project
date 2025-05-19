#!/usr/bin/env python3
"""
Linting script to check for code quality issues
"""
import os
import sys
import subprocess
from typing import List, Tuple

def run_command(command: List[str]) -> Tuple[str, str, int]:
    """Run a shell command and return stdout, stderr, and return code"""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

def print_section(title: str):
    """Print a section title"""
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80 + "\n")

def main():
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(project_root, "src")

    # Files to check
    python_files = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    has_errors = False

    # Run pylint
    print_section("Running Pylint")
    for file in python_files:
        stdout, stderr, rc = run_command(["pylint", file])
        if rc != 0:
            has_errors = True
            print(f"Issues in {os.path.basename(file)}:")
            print(stdout or stderr)

    # Run mypy for type checking
    print_section("Running MyPy Type Checker")
    stdout, stderr, rc = run_command(["mypy", src_dir])
    if rc != 0:
        has_errors = True
        print(stdout or stderr)

    # Run flake8 for style guide enforcement
    print_section("Running Flake8")
    stdout, stderr, rc = run_command(["flake8", src_dir])
    if rc != 0:
        has_errors = True
        print(stdout or stderr)

    # Run black in check mode
    print_section("Checking Code Formatting (black)")
    stdout, stderr, rc = run_command(["black", "--check", src_dir])
    if rc != 0:
        has_errors = True
        print(stdout or stderr)
        print("\nTo fix formatting issues, run: black src/")

    if has_errors:
        print("\n❌ Code quality issues were found.")
        sys.exit(1)
    else:
        print("\n✅ All checks passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
