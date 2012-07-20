#!/usr/bin/env python

from distutils.core import setup

version = open('VERSION', 'r').read().strip()

setup(name='TileExpire',
      version=version,
      packages=['TileExpire'],
      py_modules = ['TileExpire.Tiler'],
      scripts=['scripts/tileexpire-serve.py', 'scripts/tileexpire-client.py'])
