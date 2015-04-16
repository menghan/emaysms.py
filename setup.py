#!/usr/bin/env python

from distutils.core import setup

setup(
    name='emaysms',
    version='1.0',
    description='Python client for Emay.cn SMS service using HTTP SDK',
    long_description=open('README').read(),
    author='menghan',
    author_email='menghan412@gmail.com',
    url='https://github.com/menghan/emaysms.py',
    packages=['emaysms'],
    entry_points={
        'console_scripts': [
            'emaysms = emaysms.main:main',
        ]
    }

)
