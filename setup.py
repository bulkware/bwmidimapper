#!/usr/bin/env python

# Python imports
import os
from setuptools import setup

setup(
    author="Antti-Pekka Meronen (bulkware)",
    author_email="antice@kapsi.fi",
    description="A tool to convert MIDI files between different drum mappings.",
    entry_points={
        "console_scripts": [
            "bwmidimapper = bwmidimapper:main"
        ]
    },
    install_requires=[
        "mido",
        "pycodestyle",
        "pytest",
        "setuptools"
    ],
    license="GPLv3",
    name="bwmidimapper",
    py_modules=["bwmidimapper"],
    version="1.0.0",
    url="https://github.com/bulkware/bwmidimapper"
)
