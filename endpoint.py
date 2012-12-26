import redis
import urlparse
import requests
import json
import datetime
from requests.exceptions import ConnectionError
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from utils import dispatch_request, send_notification
from settings import SMTP_STATUS, SERVER_UNREACHABLE

class EndPoint(object):
    def __init__(self, config, reader):
        self.redis = redis.Redis(config['redis_host'],
                                 config['redis_port'])
        self.test_mode = config['test_mode']
        self.endpoints = reader.get_calls()
        self.url_map = Map([
            
            Rule('/endpoints/', endpoint='get_batch'),
            Rule('/endpoints/<int:id>', endpoint='get_instance'),
            Rule('/endpoints/<alias>', endpoint='get_instance')
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
        block['match'] = False
        block['requested_at'] = str(datetime.datetime.now())
        if mode == 'invalid_url':
            block['log'] = 'Sorry, but this address does\'t seem valid'
        else:
            block['log'] = 'Sorry, but an unexpected error occurred.'

        return block

    def map_response(self, response, block):
        block['url'] = response.url
        block['status'] = response.status_code
        block['requested_at'] = str(datetime.datetime.now())

    def make_request(self, endpoint):
        if endpoint['method'] == 'GET':
            return requests.get(endpoint['url']), 'get'
        elif endpoint['method'] == 'POST':
            try:
                data = endpoint['config']['request-body']
            except:
                data = None
            return requests.post(endpoint['url'], data), 'post'
        elif endpoint['method'] == 'PUT':
            try:
                data = endpoint['config']['request-body']
            except:
                data = None
            return requests.put(endpoint['url'], data=json.dumps(data)), 'put'
        else:
            raise NotImplemented('Method not recognized')
    
    def process_call(self, endpoint):
        block = {}
        if self._is_valid_url(endpoint['url']):
            counter = 0
            try:
                response, block['method'] = self.make_request(endpoint)
            except ConnectionError:
                return SERVER_UNREACHABLE
            else:
                while True:
                    self.map_response(response, block)
                    if self._is_expected(endpoint, block):
                        block['match'] = True
                        break
                    elif self._should_retry(endpoint, counter):
                        counter += 1
                    else:
                        block['match'] = False
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
        counter = 0
        if 'id' in values and values.get('id', 0) > 0:
            try:
                endpoint = self.endpoints[values['id'] - 1]
            except IndexError:
                pass
            else:
                block = self.process_call(endpoint)
        elif 'alias' in values:
            while counter < len(self.endpoints):
                endpoint = self.endpoints[counter]
                if endpoint['alias'] == values['alias']:
                    block = self.process_call(endpoint)
                    break
                counter += 1
            
        return Response(json.dumps(block))
        