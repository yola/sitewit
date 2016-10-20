#!/usr/bin/env python
from setuptools import setup
import sitewit


setup(
    name=sitewit.__name__,
    version=sitewit.__version__,
    description=sitewit.__doc__,
    author='Yola',
    author_email='engineers@yola.com',
    url=sitewit.__url__,
    packages=['sitewit'],
    install_requires=[
        'suds == 0.4',
        'demands >= 4.0.0, < 5.0.0',
        'python-dateutil < 3.0.0',
        'yoconfig < 0.3.0'
    ]
)
