#! /usr/bin/env python3

from distutils.core import setup

setup(
    name='wsgilib',
    version='latest',
    author='Richard Neumann',
    py_modules=['strflib'],
    license=open('LICENSE').read(),
    description='A simple (U)WSGI framework')
