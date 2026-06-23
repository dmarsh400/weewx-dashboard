#!/usr/bin/env python3
"""
Setup script for WeeWX Dashboard.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text()

setup(
    name="weewx-dashboard",
    version="1.0.0",
    author="WeeWX Dashboard Contributors",
    description="Cross-platform GUI dashboard for WeeWX monitoring and Weather Underground uploads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://example.com/weewx-dashboard",
    packages=find_packages(where="src"),
    py_modules=["main", "config", "weewx_db"],
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.5.0",
        "matplotlib>=3.7.0",
    ],
    entry_points={
        "console_scripts": [
            "weewx-dashboard=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
