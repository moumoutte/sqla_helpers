# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import sqla_helpers

try:
    long_description = open('doc/sqla_helpers.rst').read(),
except IOError:
    long_description = ''

setup(
    name='sqla_helpers',
    version=sqla_helpers.__version__,
    author='Guillaume Camera',
    author_email='camera.g@gmail.com',
    description="Provide some methods for getting objects with SQLAlchemy",
    long_description=long_description,
    url="https://github.com/moumoutte/sqla_helpers/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    requires=[
        'nose',
        'coverage',
        'mock',
        'sqlalchemy'
    ]
)
