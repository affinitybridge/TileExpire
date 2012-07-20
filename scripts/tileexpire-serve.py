#!/usr/bin/env python

if __name__ == '__main__':
    from optparse import OptionParser, OptionValueError
    import os, sys

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="file", default="tilestache.cfg",
        help="the path to the tilestache config")
    parser.add_option("-i", "--ip", dest="ip", default="127.0.0.1",
        help="the IP address to listen on")
    parser.add_option("-p", "--port", dest="port", type="int", default=8080,
        help="the port number to listen on")
    parser.add_option('--include-path', dest='include',
        help="Add the following colon-separated list of paths to Python's include path (aka sys.path)")
    (options, args) = parser.parse_args()

    if options.include:
        for p in options.include.split(':'):
            sys.path.insert(0, p)

    from werkzeug.serving import run_simple
    from TileExpire import Expire
    import TileStache

    if not os.path.exists(options.file):
        print >> sys.stderr, "Config file not found. Use -c to pick a tilestache config file."
        sys.exit(1)

    app = Expire(TileStache.WSGITileServer(config=options.file, autoreload=True))
    run_simple(options.ip, options.port, app, use_debugger=True, use_evalex=True, use_reloader=True)
