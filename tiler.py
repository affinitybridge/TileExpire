import logging

from TileStache import getTile
from TileStache.Core import KnownUnknown

from ModestMaps.Core import Coordinate
from ModestMaps.Geo import Location

class Manager(object):

    def __init__(self, config, verbose=True):
        self.verbose = verbose
        self.config = config
        self.layers = []

    def addLayer(self, layer, reset=False):
        if layer in ('ALL', 'ALL LAYERS') and layer not in self.config.layers:
            # clean every layer in the config
            self.layers = self.config.layers.values()

        elif layer not in self.config.layers:
            # TODO: Raise missing layer exception.
            raise KnownUnknown('"%s" is not a layer I know about. Here are some that I do know about: %s.' % (layer, ', '.join(sorted(self.config.layers.keys()))))

        else:
            if (reset):
                # clean just one layer in the config
                self.layers[self.config.layers[layer]]
            else:
                self.layers.append(self.config.layers[layer])

        return self


    def __call__(self,
              zooms=[0, 1, 2, 3],
              bbox=[85, -180, -85, 180],
              extension='png',
              padding=0):

        lat1, lon1, lat2, lon2 = bbox
        south, west = min(lat1, lat2), min(lon1, lon2)
        north, east = max(lat1, lat2), max(lon1, lon2)

        northwest = Location(north, west)
        southeast = Location(south, east)

        if padding < 0:
            raise KnownUnknown('A negative padding will not work.')

        for layer in self.layers:
            ul = layer.projection.locationCoordinate(northwest)
            lr = layer.projection.locationCoordinate(southeast)

            coordinates = generateCoordinates(ul, lr, zooms, padding)

            for (offset, count, coord) in coordinates:
                path = '%s/%d/%d/%d.%s' % (layer.name(), coord.zoom, coord.column, coord.row, extension)

                progress = {"tile": path,
                            "offset": offset + 1,
                            "total": count}

                if self.verbose:
                    logging.info('%(offset)d of %(total)d...' % progress)

                try:
                    mimetype, format = layer.getTypeByExtension(extension)
                except:
                    #
                    # It's not uncommon for layers to lack support for certain
                    # extensions, so just don't attempt to remove a cached tile
                    # for an unsupported format.
                    #
                    pass
                else:
                    yield(layer, coord, format, progress)


class Cache(object):

    def __init__(self, verbose=True):
        self.verbose = verbose


    def clean(self, tiles):
        status = []
        for (layer, coord, format, progress) in tiles:
            layer.config.cache.remove(layer, coord, format)

            if self.verbose:
                logging.info('%(tile)s' % progress)

            status.append(progress['tile'])

        return status


    def seed(self, tiles,
             ignore_cached=False,
             callback=None,
             enable_retries=True):

        status = []
        error_list = []

        for (layer, coord, format, progress) in tiles:
            #
            # Fetch a tile.
            #

            attempts = enable_retries and 3 or 1
            rendered = False

            while not rendered:
                if self.verbose:
                    logging.info('%(offset)d of %(total)d...' % progress)

                try:
                    mimetype, content = getTile(layer, coord, format, ignore_cached)

                    if 'json' in mimetype and callback:
                        js_path = '%s/%d/%d/%d.js' % (layer.name(), coord.zoom, coord.column, coord.row)
                        js_body = '%s(%s);' % (callback, content)
                        js_size = len(js_body) / 1024
                        
                        layer.config.cache.save(js_body, layer, coord, 'JS')
                        logging.info('%s (%dKB)' % (js_path, js_size))

                    elif callback:
                        print >> stderr, '(callback ignored)',

                except:
                    #
                    # Something went wrong: try again? Log the error?
                    #
                    attempts -= 1

                    if self.verbose:
                        print >> stderr, 'Failed %s, will try %s more.' % (progress['tile'], ['no', 'once', 'twice'][attempts])

                    if attempts == 0:
                        msg = '%(zoom)d/%(column)d/%(row)d\n' % coord.__dict__
                        logging.error(msg)
                        error_list.append(msg)
                        break

                else:
                    #
                    # Successfully got the tile.
                    #
                    rendered = True
                    progress['size'] = '%dKB' % (len(content) / 1024)

                    if self.verbose:
                        logging.info('%(tile)s (%(size)s)' % progress)

            status.append(progress['tile'])

        return (status, error_list)


def generateCoordinates(ul, lr, zooms, padding):
    """ Generate a stream of (offset, count, coordinate) tuples for seeding.
    
        Flood-fill coordinates based on two corners, a list of zooms and padding.
    """
    # start with a simple total of all the coordinates we will need.
    count = 0
    
    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)
        
        rows = lr_.row + 1 - ul_.row
        cols = lr_.column + 1 - ul_.column
        
        count += int(rows * cols)

    # now generate the actual coordinates.
    # offset starts at zero
    offset = 0
    
    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)

        for row in range(int(ul_.row), int(lr_.row + 1)):
            for column in range(int(ul_.column), int(lr_.column + 1)):
                coord = Coordinate(row, column, zoom)
                
                yield (offset, count, coord)
                
                offset += 1
