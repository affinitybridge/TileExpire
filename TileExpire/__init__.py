import json

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule, RequestRedirect
from werkzeug.exceptions import HTTPException, NotFound, BadRequest

from Tiler import Tiles, Cache

class Expire(object):

    def __init__(self, app):
        self.app = app
        self.url_map = Map([
            Rule('/clean/<layer>', endpoint='clean'),
            Rule('/seed/<layer>', endpoint='seed')
        ])


    def clean(self, request, layer):
        """
        zooms=[0, 1, 2, 3]
        bbox=[85, -180, -85, 180]
        extension='png'
        padding=0
        """

        tiles = Tiles(self.app.config).addLayer(layer)
        params = self.params(request.data)
        tiles = Cache().clean(tiles(**params))

        results = {
            'tiles': len(tiles)
        }
        return Response("%(tiles)d tiles cleared from cache." % results)


    def seed(self, request, layer):
        """
        zooms=[0, 1, 2, 3]
        bbox=[85, -180, -85, 180]
        extension='png'
        padding=0
        """

        tiles = Tiles(self.app.config).addLayer(layer)
        params = self.params(request.data)
        tiles, errors = Cache().seed(tiles(**params))

        results = {
            'tiles': len(tiles),
            'errors': len(errors)
        }
        return Response("%(tiles)d tiles seeded, %(errors)d errors occured" % results)


    def params(self, raw):
        data = json.loads(raw)
        params = {}

        if 'bbox' in data:
            params['bbox'] = data['bbox']

        if 'zooms' in data:
            params['zooms'] = []
            for (i, zoom) in enumerate(data['zooms']):
                if not zoom.isdigit():
                    raise Exception('"%s" is not a valid numeric zoom level.' % zoom)
                params['zooms'].append(int(zoom))

        if 'extension' in data:
            params['extension'] = data['extension']

        if 'padding' in data:
            if (data['padding'] < 0):
                raise Exception('A negative padding will not work.')
            params['padding'] = data['padding']

        return params


    def __call__(self, environ, start_response):
        urls = self.url_map.bind_to_environ(environ)

        try:
            endpoint, args = urls.match()
            response = getattr(self, endpoint)(Request(environ), **args)
            return response(environ, start_response)

        except NotFound as e:
            # Fallback to tilestache.
            return self.app(environ, start_response)

        except HTTPException, e:
            return e(environ, start_response)


