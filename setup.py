#!/usr/bin/env python
from setuptools import setup

import sitewit

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name=sitewit.__name__,
    version=sitewit.__version__,
    description=sitewit.__doc__,
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Yola',
    author_email='engineers@yola.com',
    url=sitewit.__url__,
    packages=['sitewit'],
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'demands >= 4.0.0, < 6.0.0',
        'python-dateutil < 3.0.0',
        'yoconfig < 0.3.0'
    ]
)
