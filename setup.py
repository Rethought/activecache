#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "activecache",
    version = "0.1.3",
    author = "ReThought Ltd",
    author_email = "code@rethought-solutions.com",
    url = "git://github.com/Rethought/activecache",

    package_dir = {'':'src'},
    py_modules = ['activecache'],
    license = "BSD",
    keywords = "cache",
    description = "Active in-memory cache object for Python.",
    classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
