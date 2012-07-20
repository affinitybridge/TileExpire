from distutils.core import setup
setup(name='TileExpire',
      version='0.0.1',
      packages=['TileExpire'],
      py_modules = ['TileExpire.Tiler'],
      scripts=['scripts/tileexpire-serve.py', 'scripts/tileexpire-client.py'])
