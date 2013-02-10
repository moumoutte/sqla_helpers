# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import sqla_helpers

setup(
    name='sqla_helpers',
    version=sqla_helpers.__version__,
    author='Guillaume Camera',
    author_email='camera.g@gmail.com',
    description="Fournit quelques méthodes de récupération d'objet en base autour d'SQLAlchemy",
    long_description=open('doc/sqla_helpers.rst').read(),
    url="https://github.com/moumoutte/sqla_helpers/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications",
    ],
    requires=[
        'nose',
        'coverage',
        'mock',
        'sqlalchemy'
    ]
)
