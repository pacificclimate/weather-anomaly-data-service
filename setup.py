import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

__version__ = (1, 0, 0)

setup(
    name="wads",
    description="PCIC microservice for weather anomaly data",
    keywords="sql database pcds crmp climate meteorology",
    packages=find_packages(),
    version='.'.join(str(d) for d in __version__),
    url="http://www.pacificclimate.org/",
    author="Rod Glover",
    author_email="rglover@uvic.ca",
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-Cors',
        'PyCDS',  # TODO: Add version requirement once versioning with WA tables and views has been set
    ],
    zip_safe=True,
    scripts=['scripts/devserver.py'],
    tests_require=['pytest', 'testing.postgresql'],
    classifiers='''Development Status :: 2 - Pre-Alpha
Environment :: Web Environment
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Operating System :: OS Independent
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Topic :: Internet
Topic :: Scientific/Engineering
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules'''.split('\n')
)
