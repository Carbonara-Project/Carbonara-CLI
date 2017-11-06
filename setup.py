#!/usr/bin/env python

__author__ = "Andrea Fioraldi, Luigi Paolo Pileggi"
__copyright__ = "Copyright 2017, Carbonara Project"
__license__ = "BSD 2-clause"
__email__ = "andreafioraldi@gmail.com, willownoises@gmail.com"

from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='carbonara-cli',
    version="1.0alpha",
    license=__license__,
    description='CLI interface for Carbonara',
    long_description=readme,
    author=__author__,
    author_email=__email__,
    url='https://github.com/Carbonara-Project/Carbonara-CLI',
    package_dir={'carbonara-cli': 'carbonara-cli'},
    packages=['carbonara-cli'],
    scripts=['carbonara-cli.py'],
    dependency_links=['https://github.com/Carbonara-Project/Guanciale/tarball/master#egg=guanciale-1.0']
)

