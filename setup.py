"""A package to retrieve information and download some files from the dbGaP ftp server."""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dbgap-ftp',
    version='1.0.0',
    description='Retrieve information and download files from dbGaP\'s ftp server',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/UW-GAC/dbgap_ftp',
    author='Adrienne Stilp',
    license='MIT',
    keywords='dbgap',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>3',
)
