#!/usr/bin/env python

from sys import stderr
from optparse import OptionParser
from httplib import HTTPConnection
import json

parser = OptionParser(usage="""%prog [options] method [zooms]

""")

defaults = dict(padding=1, bbox=(85, -180, -85, 180), extension='png')
parser.set_defaults(**defaults)

parser.add_option('-l', '--layer', dest='layer',
                  help='Layer name from configuration, typically required.')

parser.add_option('-b', '--bbox', dest='bbox',
                  help='Bounding box in floating point geographic coordinates: south west north east. Default value is %.3f, %.3f, %.3f, %.3f.' % defaults['bbox'],
                  type='float', nargs=4)

parser.add_option('-p', '--padding', dest='padding',
                  help='Extra margin of tiles to add around bounded area. Default value is %s (no extra tiles).' % repr(defaults['padding']),
                  type='int')

parser.add_option('-e', '--extension', dest='extension',
                  help='Optional file type for rendered tiles. Default value is "png" for most image layers and some variety of JSON for Vector or Mapnik Grid providers.')


if __name__ == '__main__':
    options, args = parser.parse_args()

    if len(args) == 0 or args[0] not in ('clean', 'seed'):
        raise Exception('Invalid method. Must be "clean" or "seed"')
    else:
        method = args.pop(0)
        zooms = args

    if options.layer is None:
        raise Exception('Missing required layer (--layer) parameter.')

    elif options.padding < 0:
        raise Exception('A negative padding will not work.')

    payload = {
        'zooms': zooms,
        'bbox': options.bbox,
        'extension': options.extension,
        'padding': options.padding
    }

    conn = HTTPConnection('localhost', 8080)
    conn.connect()

    conn.request('POST', '/' + method + '/' + options.layer, json.dumps(payload))

    response = conn.getresponse()
    print >> stderr, 'Status: %(status)d - %(reason)s' % \
            {'status': response.status, 'reason': response.reason}

    data = response.read()
    print >> stderr, data

    conn.close()
