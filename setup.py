"""
Setup script for THRESHOLD_ONSET package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="threshold-onset",
    version="1.2.0",
    author="ChavalaSantosh",
    author_email="santoshysc@gmail.com",
    maintainer="ChavalaSantosh",
    maintainer_email="santoshysc@gmail.com",
    description="A foundational system exploring structure emergence through action, trace, and repetition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chavalasantosh/THRESHOLDONSET",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core system uses Python standard library only
        # Optional dependencies for version control tools
    ],
    extras_require={
        "dev": [
            "pylint>=3.0.0",
            "watchfiles>=0.21.0",
        ],
        "all": [
            "pylint>=3.0.0",
            "watchfiles>=0.21.0",
            "numpy",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "threshold-onset=threshold_onset.cli:main",
        ],
    },
)
