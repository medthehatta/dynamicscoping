#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Setup python environment."""


from setuptools import find_packages, setup


INSTALL_REQUIREMENTS = []
SCRIPT_NAMES = []


def get_version():
    """Return the version."""
    return "0.1"


def _console_script(name):
    """Return the default format for a console script declaration."""
    return '{name}={package}.{name}:main'.format(
        name=name,
        package='dynamicscoping',
    )


setup(
    name='dynamicscoping',
    version=get_version(),
    description='',
    long_description=open('README.rst').read(),
    author='Med Mahmoud',
    author_email='medthehatta@gmail.com',
    url='https://github.com/medthehatta/dynamicscoping',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Networking',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=INSTALL_REQUIREMENTS,
    entry_points={
        'console_scripts': [_console_script(name) for name in SCRIPT_NAMES],
    },
)
