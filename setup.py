# encoding: utf-8
#
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
# Get current version from the VERSION file
with open(os.path.join(here, 'VERSION')) as fv:
    version = fv.read()

setup(
    name='wapi-python',
    packages=['wapi'],
    install_requires=[
        'requests >= 2.18',
        'sseclient >= 0.0.18',
        'pytz',
        'pandas >= 0.21',
        'future >= 0.16',
    ],
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
