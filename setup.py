#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

setup_requirements = ['pytest-runner', ]

setup(
    author="Shiva Adirala",
    author_email='adiralashiva8@gmail.com',
    description='Live results for pytest',
    long_description='Generate live execution results using pytest hook',
    classifiers=[
        'Framework :: Pytest',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
    ],
    license="MIT license",
    include_package_data=True,
    keywords=[
        'pytest', 'py.test', 'live',
    ],
    name='pytest-live',
    packages=find_packages(include=['pytest_live']),
    setup_requires=setup_requirements,
    url='https://github.com/adiralashiva8/pytest-live-results',
    version='0.1',
    zip_safe=True,
    install_requires=[
        'pytest',
        'pytest-runner'
    ],
    entry_points={
        'pytest11': [
            'pytest-live = pytest_live.plugin',
        ]
    }
)