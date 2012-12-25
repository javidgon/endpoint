import redis
import urlparse
import requests
import json
import datetime
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from utils import dispatch_request, send_notification
from settings import SMTP_STATUS

class EndPoint(object):
    def __init__(self, config, reader):
        self.redis = redis.Redis(config['redis_host'],
                                 config['redis_port'])
        self.test_mode = config['test_mode']
        self.endpoints = reader.get_calls()
        self.url_map = Map([
            Rule('/endpoints/', endpoint='get_batch'),
            Rule('/endpoints/<int:id>', endpoint='get_instance'),
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
        block['date'] = str(datetime.datetime.now())
        if mode == 'invalid_url':
            block['log'] = 'Sorry, but this address does\'t seem valid'
        else:
            block['log'] = 'Sorry, but an unexpected error occurred.'

        return block

    def map_response(self, response):
        block = {}
        block['url'] = response.url
        block['status'] = response.status_code
        block['date'] = str(datetime.datetime.now())

        return block

    def make_request(self, endpoint):      
        return requests.get(endpoint['url'])
    
    def process_call(self, endpoint):
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
                    if not self.test_mode and SMTP_STATUS:
                        block['log'] = send_notification()
                    break
        else:
            block = self._generate_error_response(endpoint, 'invalid_message')
            
        return block

    def get_batch(self, request, **values):
        cube = []
        limit = None
        if 'limit' in dict(request.args).keys():
            limit = int(request.args['limit'])
        for endpoint in self.endpoints:
            if limit != None:
                limit = limit - 1
                if limit == -1:
                    break
            cube.append(self.process_call(endpoint))

        return Response(json.dumps(cube))
    
    def get_instance(self, request, **values):
        block = []
        if 'id' in values:
            try:
                endpoint = self.endpoints[values['id']]
            except IndexError:
                pass
            else:
                block = self.process_call(endpoint)
            
        return Response(json.dumps(block))
        