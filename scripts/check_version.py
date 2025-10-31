#!/usr/bin/env python3
"""Check that __init__.py version matches pyproject.toml version."""

import sys
import tomllib
from pathlib import Path


def main():
    # Read version from pyproject.toml
    pyproject_path = Path("pyproject.toml")
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)
    pyproject_version = pyproject["project"]["version"]

    # Read version from __init__.py
    init_path = Path("src/shinkuro/__init__.py")
    init_content = init_path.read_text()

    # Extract __version__ from __init__.py
    for line in init_content.splitlines():
        if line.startswith("__version__"):
            init_version = line.split("=")[1].strip().strip("\"'")
            break
    else:
        print("ERROR: __version__ not found in __init__.py")
        return 1

    if pyproject_version != init_version:
        print("ERROR: Version mismatch!")
        print(f"  pyproject.toml: {pyproject_version}")
        print(f"  __init__.py: {init_version}")
        return 1

    print(f"✓ Version consistency check passed: {pyproject_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
