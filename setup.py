#!/usr/bin/env python

__author__ = "Andrea Fioraldi, Luigi Paolo Pileggi"
__copyright__ = "Copyright 2017, Carbonara Project"
__license__ = "BSD 2-clause"
__email__ = "andreafioraldi@gmail.com, willownoises@gmail.com"

from setuptools import setup

VER = "1.0.10"

setup(
    name='carbonara_cli',
    version=VER,
    license=__license__,
    description='CLI interface for Carbonara',
    author=__author__,
    author_email=__email__,
    url='https://github.com/Carbonara-Project/Carbonara-CLI',
    download_url = 'https://github.com/Carbonara-Project/Carbonara-CLI/archive/' + VER + '.tar.gz',
    package_dir={'carbonara_cli': 'carbonara_cli'},
    packages=['carbonara_cli'],
    install_requires=[
        'progressbar2',
        'guanciale'
    ],
    entry_points={
        'console_scripts': [
            'carbonara_cli = carbonara_cli.main:main',
            'carb = carbonara_cli.main:main'
        ]
    },
)

