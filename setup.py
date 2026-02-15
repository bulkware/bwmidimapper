#!/usr/bin/env python

"""
bwMIDIMapper
A tool to convert MIDI files between different drum mappings.
"""

# Python imports
from setuptools import find_packages, setup

setup(
    author="Antti-Pekka Meronen (bulkware)",
    author_email="antice@kapsi.fi",
    description="A tool to convert MIDI files between different drum mappings.",
    entry_points={
        "console_scripts": [
            "bwmidimapper = bwmidimapper.main:main"
        ]
    },
    include_package_data=True,
    packages=find_packages(),
    package_data={"bwmidimapper": ["data/*.csv"]},
    install_requires=[
        "mido",
        "pycodestyle",
        "pylint",
        "pytest",
        "setuptools"
    ],
    license="GPLv3",
    name="bwmidimapper",
    version="1.3.0",
    url="https://github.com/bulkware/bwmidimapper"
)
