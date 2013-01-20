import urlparse
import json
import os

from requests.exceptions import ConnectionError, Timeout
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import NotImplemented
from endpoint.utils import (dispatch_request, send_notification, make_request,
                            render_response)
from endpoint.settings import SMTP_STATUS, SPECS_PATH
from endpoint.readers.yaml_reader import YamlReader

class Sentinel(object):
    """
    Sentinel will be in charge of making requests using the
    endpoints defined in the .yml file.
    """
    def __init__(self):
        self.url_map = Map([
            Rule('/', endpoint='invalid_request'),
            Rule('/<spec>/', endpoint='get_batch_of_responses'),
            Rule('/<spec>/<int:id>', endpoint='get_response'),
            Rule('/<spec>/<alias>', endpoint='get_response')
        ])

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = dispatch_request(self, request)

        return response(environ, start_response)

    def is_valid_url(self, endpoint):
        """
        Check is the passed url is valid
        """
        parts = urlparse.urlparse(endpoint)
        return parts.scheme in ('http','https')

    def should_retry(self, endpoint, counter):
        """
        Check if the sentinel should continue trying to
        get a proper response from the endpoint. This value
        is passed in the .yml file.
        """ 
        return counter == endpoint['config']['retries']

    def verify_status_code(self, endpoint, response):
        """
        Verify if the status code is the right one.
        """
        result = False
        if response.status_code == endpoint['asserts']['status-code']:
            result = True
        
        return result
   
    def process_call(self, endpoint):
        """
        Process a single request and build a response.
        """
        if self.is_valid_url(endpoint['url']):
            try:
                response = make_request(endpoint)
            except ConnectionError:
                return render_response(error='SERVER_UNREACHABLE',
                                         status_code=500,
                                         obj=endpoint)
            except NotImplemented:
                return render_response(error='NOT_IMPLEMENTED',
                                         status_code=501,
                                         obj=endpoint)
            except Timeout:
                return render_response(error='REQUEST_TIMEOUT',
                                         status_code=408,
                                         obj=endpoint)
            else:
                tests_passed = False
                counter = 0
                while True:
                    if self.verify_status_code(endpoint, response):
                        tests_passed = True
                        break
                    elif self.should_retry(endpoint, counter):
                        counter += 1
                    else:
                        if not self.test_mode and SMTP_STATUS:
                            send_notification()
                        break
        else:
            return render_response(error='BAD_REQUEST',
                                     status_code=400,
                                     obj=endpoint)
            
        return render_response(status_code=response.status_code,
                                response=response,
                                tests_passed=tests_passed)

    def get_batch_of_responses(self, request, **values):
        """
        Get a batch of responses from the respective requests.
        """
        cube = []
        limit = None
        try:
            reader = YamlReader(values['spec'])
        except IOError:
            pass
        else:
            endpoints = reader.get_calls()
            if 'limit' in dict(request.args).keys():
                limit = int(request.args['limit'])
            for endpoint in endpoints:
                if limit != None:
                    limit = limit - 1
                    if limit == -1:
                        break
                cube.append(self.process_call(endpoint))

        return Response(json.dumps(cube))
    
    def get_response(self, request, **values):
        """
        Get a single response from a single request.
        """
        block = {}
        counter = 0
        try:
            reader = YamlReader(values['spec'])
        except IOError:
            pass
        else:
            endpoints = reader.get_calls()
            if 'id' in values and values.get('id', 0) > 0:
                try:
                    endpoint = endpoints[values['id'] - 1]
                except IndexError:
                    pass
                else:
                    block = self.process_call(endpoint)
            elif 'alias' in values:
                while counter < len(endpoints):
                    endpoint = endpoints[counter]
                    if endpoint['alias'] == values['alias']:
                        block = self.process_call(endpoint)
                        break
                    counter += 1
            
        return Response(json.dumps(block))
    
    def invalid_request(self, request, **values):
        block = {}
        
        return Response(json.dumps(block))