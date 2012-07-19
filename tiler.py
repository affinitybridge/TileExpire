import logging

from TileStache.Core import KnownUnknown

from ModestMaps.Core import Coordinate
from ModestMaps.Geo import Location

class Manager(object):

    def __init__(self, config, layer='ALL', verbose=True):
        self.verbose = verbose
        self.config = config

        if layer in ('ALL', 'ALL LAYERS') and layer not in config.layers:
            # clean every layer in the config
            self.layers = config.layers.values()

        elif layer not in config.layers:
            raise KnownUnknown('"%s" is not a layer I know about. Here are some that I do know about: %s.' % (layer, ', '.join(sorted(config.layers.keys()))))

        else:
            # clean just one layer in the config
            self.layers = [config.layers[layer]]

    def clean(self, zooms=[0, 1, 2, 3], bbox=[85, -180, -85, 180], extension='png', padding=0):
        lat1, lon1, lat2, lon2 = bbox
        south, west = min(lat1, lat2), min(lon1, lon2)
        north, east = max(lat1, lat2), max(lon1, lon2)

        northwest = Location(north, west)
        southeast = Location(south, east)

        if padding < 0:
            raise KnownUnknown('A negative padding will not work.')

        status = []
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
                    #yield (layer, coord, format, progress)
                    self.config.cache.remove(layer, coord, format)
        
                if self.verbose:
                    logging.info('%(tile)s' % progress)
                        
                # if progressfile:
                #     fp = open(progressfile, 'w')
                #     json_dump(progress, fp)
                #     fp.close()

            status.append(layer.name())

        return status


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
