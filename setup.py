#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='openwfs',
    version='0.1.0',
    description='Software and spatialisation tools for OpenWFS',
    author='Daniel Jones',
    author_email='daniel@jones.org.uk',
    url='https://github.com/open-WFS/open-WFS-software',
    packages=find_packages(),
    install_requires=['python-osc', 'mido', 'python-rtmidi', 'pandas', 'numpy', 'python-osc', 'coloredlogs'],
    keywords=['sound', 'audio', 'spatial'],
    classifiers=[
        'Topic :: Multimedia :: Sound/Audio',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-timeout']
)
