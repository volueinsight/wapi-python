# encoding: utf-8
#
import os, sys
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
# Get current version from the VERSION file
with open(os.path.join(here, 'VERSION')) as fv:
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
    description='Wattsight API python library',
    long_description='This library is meant as a simple toolkit for working with data from https://api.wattsight.com/ (or equivalent services).  Note that access is based on some sort of login credentials, this library is not all that useful unless you have a valid Wattsight account.',
    author='Wattsight',
    author_email='support@wattsight.com',
    url='https://www.wattsight.com'
)
