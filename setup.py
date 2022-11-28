# encoding: utf-8
#
import os, sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
# Get current version from the VERSION file
with open(os.path.join(here, 'VERSION')) as fv:
    version = fv.read()

install_requires = [
    'requests >= 2.18',
    'sseclient-py >= 1.7',
    'pandas >= 1.5.0',
    'future >= 0.16',
]

setup(
    name='wapi-python',
    python_requires='>=3.9',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=[
        'pytest',
        'pytest-cov >= 2.5',
        'requests-mock >= 1.3',
    ],
    version=version,
    description='Volue Insight API python library',
    long_description='This library is meant as a simple toolkit for working with data from https://api.volueinsight.com/ (or equivalent services).  Note that access is based on some sort of login credentials, this library is not all that useful unless you have a valid Volue Insight account.',
    author='Volue Insight',
    author_email='support.insight@volue.com',
    url='https://www.volueinsight.com'
)
