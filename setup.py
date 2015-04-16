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
        'demands < 2.0.0',
        'yoconfig < 0.3.0'
    ]
)
