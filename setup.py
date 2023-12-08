# encoding: utf-8
#
import os, sys
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
# Get current version from the VERSION file
with open(os.path.join(here, 'wapi/VERSION')) as fv:
    version = fv.read()

install_requires = [
    'requests >= 2.18',
    'sseclient-py >= 1.7',
    'pytz',
    'pandas >= 0.21',
    'future >= 0.16',
]
if sys.version_info < (3,):
    install_requires.append('configparser >= 3.5')

setup(
    name='wapi-python',
    packages=['wapi'],
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
