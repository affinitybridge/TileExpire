import json

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule, RequestRedirect
from werkzeug.exceptions import HTTPException, NotFound, BadRequest

import tiler

class Expire(object):

    def __init__(self, app):
        self.app = app
        self.url_map = Map([
            Rule('/clean/<layer>', endpoint='clean')
        ])

    def clean(self, request, layer):
        """
        zooms=[0, 1, 2, 3]
        bbox=[85, -180, -85, 180]
        extension='png'
        padding=0
        """
        data = json.loads(request.data)

        params = {}
        if 'bbox' in data:
            params['bbox'] = data['bbox']
        if 'zooms' in data:
            params['zooms'] = data['zooms']
        if 'extension' in data:
            params['extension'] = data['extension']
        if 'padding' in data:
            params['padding'] = data['padding']

        manager = tiler.Manager(self.app.config, layer)
        results = manager.clean(**params)

        return Response(json.dumps(results))

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


