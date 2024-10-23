#!/usr/bin/env python
from setuptools import setup

setup(
    name='PyLiveLinkFace',
    version='0.1',
    description='Python Library for sending and receiving LiveLinkFace data from Unreal Engine',
    author='Marco Pattke',
    author_email='j1m_w3st@web.de',
    url='https://github.com/JimWest/PyLiveLinkFace',
    packages=['pylivelinkface'],
    install_requires=[
        'numpy',
        'timecode'
    ],
    python_requires='>=3.6',
)
