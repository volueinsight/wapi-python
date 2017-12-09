from setuptools import setup

setup(
    name='dapi',
    packages=['dapi'],
    install_requires=[
        'pycryptodome == 3.4',
        'requests == 2.11.1',
        'sseclient == 0.0.12',
        'pytest-runner == 2.9',
        'pytz',
        'pandas == 0.18.1',
    ],
    tests_require=[
        'pytest == 3.0.2',
        'pytest-pythonpath == 0.7.1',
        'pytest-cov == 2.3.1',
        'requests-mock == 1.1.0',
    ],
    version='0.1',
    description="Wattsight data API python library",
    author='Harald Nordgård-Hansen',
    author_email='hnh@wattsight.com',
    url='http://www.wattsight.com'
)
