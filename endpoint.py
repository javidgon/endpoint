import redis
import urlparse
import requests
import json
import datetime
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from utils import dispatch_request

class EndPoint(object):
    def __init__(self, config, reader):
        self.redis = redis.Redis(config['redis_host'],
                                 config['redis_port'])
        self.endpoints = reader.get_calls()
        self.url_map = Map([
            Rule('/', endpoint='process_endpoints'),
        ])

    def __call__(self, environ, start_response):
        
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = dispatch_request(self, request)

        return response(environ, start_response)

    def _is_valid_url(self, endpoint):
        parts = urlparse.urlparse(endpoint)

        return parts.scheme in ('http','https')

    def _should_retry(self, endpoint, counter):
        
        return counter == endpoint['config']['retries']

    def _is_expected(self, endpoint, block):

        return block['status'] == endpoint['config']['expected-status']

    def _generate_error_message(self, endpoint, mode=None):
        block = {}
        block['url'] = endpoint['url']
        block['pass'] = False
        if mode == 'invalid_url':
            block['error'] = 'Sorry, but this address does\'t seem valid'
        else:
            block['error'] = 'Sorry, but an unexpected error occurred.'

        return block

    def map_response(self, response):
        block = {}
        block['url'] = response.url
        block['status'] = response.status_code
        block['date'] = str(datetime.datetime.now())

        return block

    def make_request(self, endpoint):
        
        return requests.get(endpoint['url'])

    def process_endpoints(self, request, **values):
        cube = []
        for endpoint in self.endpoints:
            if self._is_valid_url(endpoint['url']):
                counter = 0
                response = self.make_request(endpoint)
                while True:
                    block = self.map_response(response)
                    if self._is_expected(endpoint, block):
                        block['pass'] = True
                        break
                    elif self._should_retry(endpoint, counter):
                        counter += 1
                    else:
                        block['pass'] = False
                        block['log'] = 'Email sent'
                        # TODO: Send email if an address has been provided.
                        break
            else:
                block = self._generate_error_response(endpoint, 'invalid_message')
            cube.append(block)

        return Response(json.dumps(cube))
        