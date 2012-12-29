import urlparse
import json

from requests.exceptions import ConnectionError
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from endpoint.utils.utils import (dispatch_request, send_notification, make_request,
                                  build_response, render_http_error)
from endpoint.settings.settings import SMTP_STATUS

class Sentinel(object):
    def __init__(self, config, reader):
        self.test_mode = config['test_mode']
        self.endpoints = reader.get_calls()
        self.url_map = Map([
            Rule('/', endpoint='get_batch'),
            Rule('/<int:id>', endpoint='get_instance'),
            Rule('/<alias>', endpoint='get_instance')
        ])

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = dispatch_request(self, request)

        return response(environ, start_response)

    def is_valid_url(self, endpoint):
        parts = urlparse.urlparse(endpoint)
        return parts.scheme in ('http','https')

    def should_retry(self, endpoint, counter): 
        return counter == endpoint['config']['retries']

    def test_response(self, endpoint, response):
        result = False
        if response.status_code == endpoint['asserts']['status-code']:
            result = True
        
        return result
   
    def process_call(self, endpoint):
        if self.is_valid_url(endpoint['url']):
            try:
                response = make_request(endpoint)
            except (ConnectionError, NotImplemented):
                return render_http_error('SERVER_UNREACHABLE',
                                         500,
                                         endpoint['asserts']['status-code'])
            else:
                tests_passed = False
                log = None
                counter = 0
                while True:
                    if self.test_response(endpoint, response):
                        tests_passed = True
                        break
                    elif self.should_retry(endpoint, counter):
                        counter += 1
                    else:
                        if not self.test_mode and SMTP_STATUS:
                            send_notification()
                        break
        else:
            return render_http_error('INVALID_URL',
                                     400,
                                     endpoint['asserts']['status-code'])
            
        return build_response(response, tests_passed)

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
        block = {}
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