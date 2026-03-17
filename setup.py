#!/usr/bin/env python3
# HELIOSICA Setup Script
# Heliospheric Event and L1 Integrated Observatory for Solar Intelligence and Coronal Activity
# Version: 1.0.0 | DOI: 10.5281/zenodo.19042948

import os
import sys
from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Read version
version = "1.0.0"

setup(
    name="heliosica",
    version=version,
    author="Samir Baladi",
    author_email="gitdeeper@gmail.com",
    description="HELIOSICA: Nine Parameters to Decode the Solar Wind and Shield Our Digital World",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitdeeper9/heliosica",
    project_urls={
        "Documentation": "https://heliosica.netlify.app/docs",
        "Source": "https://github.com/gitdeeper9/heliosica",
        "Bug Reports": "https://github.com/gitdeeper9/heliosica/issues",
        "Discussion": "https://github.com/gitdeeper9/heliosica/discussions",
        "DOI": "https://doi.org/10.5281/zenodo.19042948",
        "Web Dashboard": "https://heliosica.netlify.app",
    },
    packages=find_packages(include=["heliosica", "heliosica.*"]),
    install_requires=requirements,
    python_requires=">=3.9, <3.12",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords="space-weather heliophysics cme solar-wind geomagnetic-storm kp-index dst-index dbm",
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "heliosica=heliosica.cli.main:cli",
            "heliosica-download=heliosica.cli.download:main",
            "heliosica-process=heliosica.cli.process:main",
            "heliosica-gssi=heliosica.cli.gssi:main",
            "heliosica-serve=heliosica.cli.serve:main",
            "heliosica-diagnostic=heliosica.cli.diagnostic:main",
            "heliosica-validate=heliosica.cli.validate:main",
            "heliosica-forecast=heliosica.cli.forecast:main",
            "heliosica-alert=heliosica.cli.alert:main",
            "heliosica-dbm=heliosica.cli.dbm:main",
            "heliosica-kp=heliosica.cli.kp:main",
            "heliosica-magnetopause=heliosica.cli.magnetopause:main",
            "heliosica-forbush=heliosica.cli.forbush:main",
        ],
        "heliosica.physics": [
            "dbm = heliosica.physics.dbm:DragBasedModel",
            "magnetopause = heliosica.physics.magnetopause:MagnetopauseTracker",
            "reconnection = heliosica.physics.reconnection:ReconnectionElectricField",
            "kp_predictor = heliosica.physics.kp_predictor:KpPredictor",
            "forbush = heliosica.physics.forbush:ForbushDecrease",
            "gssi = heliosica.physics.gssi:GeomagneticStormSeverityIndex",
        ],
        "heliosica.data": [
            "dscovr = heliosica.data.loaders.dscovr:DSCOVRLoader",
            "soho = heliosica.data.loaders.soho:SOHOLoader",
            "omni = heliosica.data.loaders.omni:OMNILoader",
            "nmdb = heliosica.data.loaders.nmdb:NMDBLoader",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
        ],
        "web": [
            "flask>=2.3.0",
            "dash>=2.9.0",
            "gunicorn>=20.1.0",
        ],
        "ml": [
            "tensorflow>=2.13.0",
            "pytorch>=2.0.0",
            "xgboost>=1.7.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=6.0.0",
            "sphinx>=7.0.0",
            "flask>=2.3.0",
            "dash>=2.9.0",
            "tensorflow>=2.13.0",
        ],
    },
    platforms=["any"],
    license="MIT",
)

print("✅ HELIOSICA setup complete!")
print(f"☀️ Version: {version}")
print("📚 Documentation: https://heliosica.netlify.app/docs")
print("🐍 Python: >=3.9, <3.12")
print("🛰️ SPIN Parameters: 9 | GSSI Accuracy: 88.4%")
