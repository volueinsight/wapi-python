import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
# Get current version from the VERSION file
with open(os.path.join(here, 'VERSION')) as fv:
    version = fv.read()

setup(
    name='wapi',
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
    description="Wattsight API python library",
    author='Harald Nordgard-Hansen',
    author_email='hnh@wattsight.com',
    url='http://www.wattsight.com'
)
