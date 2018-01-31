from setuptools import setup

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
    version='0.2',
    description="Wattsight API python library",
    author='Harald Nordgård-Hansen',
    author_email='hnh@wattsight.com',
    url='http://www.wattsight.com'
)
