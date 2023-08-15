# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 13:54:18 2023

@author: stefa
"""

from setuptools import setup, find_packages


setup(
    name='pylynx',
    version='0.1',
    license='MIT',
    packages=find_packages(exclude="references"),
    description='Python for Dynamic Device Lynx',
    url='https://github.com/stefangolas/pylynx.git',
    author='Stefan Golas',
    author_email='stefanmgolas@gmail.com',
    entry_points={
        'console_scripts': [
            'pylynx-new-project = pylynx.template_creator:create_project',
            'pylynx-configure = pylynx.auto_configure:auto_configure'
        ],
    },
)
