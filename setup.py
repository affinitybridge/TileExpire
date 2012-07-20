#!/usr/bin/env python

from distutils.core import setup

version = open('VERSION', 'r').read().strip()

setup(name='TileExpire',
      version=version,
      description='Experimental cache manager middleware for TileStache.',
      author='Tom Nightingale',
      author_email='tom@affinitybridge.com',
      url='http://affinitybridge.com',
      requires=['ModestMaps (>=1.3.0)', 'TileStache (>=1.38.0)', 'werkzueg'],
      packages=['TileExpire'],
      py_modules = ['TileExpire.Tiler'],
      scripts=['scripts/tileexpire-serve.py', 'scripts/tileexpire-client.py'])
