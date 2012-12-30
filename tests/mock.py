import json
import datetime

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.http import (parse_authorization_header,
                           parse_www_authenticate_header)
from werkzeug.exceptions import Unauthorized, Forbidden
from endpoint.contrib.authdigest import RealmDigestDB
from endpoint.utils import dispatch_request

class Mock(object):
    def __init__(self):
        self.url_map = Map([
            Rule('/mock/', endpoint='get_method'),
            Rule('/mock/post', endpoint='post_method'),
            Rule('/mock/put/<int:id>', endpoint='put_method'),
            Rule('/mock/post/basic-auth', endpoint='basic_auth_mock'),
            Rule('/mock/post/digest-auth', endpoint='digest_auth_mock'),
            
        ])
        self.authDB = RealmDigestDB('test-realm')
        self.authDB.add_user('dev', 'example')

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = dispatch_request(self, request)

        return response(environ, start_response)

    def get_method(self, request, **values):
        example = {
                   "name": "This is a JSON obj created just for the GET method.", 
                   "status": 200,
                   "requested_at": str(datetime.datetime.now()),
                   }

        return Response(json.dumps(example))
    
    def post_method(self, request, **values):
        example = {
                   "name": "Created new resource.", 
                   "status": 200,
                   "requested_at": str(datetime.datetime.now()),
                   "body": json.dumps(request.form)
                   }
        
        return Response(json.dumps(example))
            
    def basic_auth_mock(self, request, **values):
        example = {
                   "name": "Wow! You got in a restricted area with security level 1 (Basic auth)", 
                   "status": 200,
                   "requested_at": str(datetime.datetime.now()),
                   "body": json.dumps(request.form)
                   }
        
        if 'Authorization' in request.headers:
            auth = parse_authorization_header(request.headers['Authorization'])
            try:
                if auth['username'] == 'dev' and auth['password'] == 'example':
                    return Response(json.dumps(example))
            except KeyError:
                pass
       
        raise Unauthorized
            
    def digest_auth_mock(self, request, **values):
        example = {
                   "name": "Wow! You got in a restricted area with security level 2 (Digest auth)", 
                   "status": 200,
                   "requested_at": str(datetime.datetime.now()),
                   "body": json.dumps(request.form)
                   }
        
        if 'Authorization' in request.headers:
            if self.authDB.isAuthenticated(request):
                return Response(json.dumps(example))
            else:
                raise Unauthorized
            
        return self.authDB.challenge()
    
    def put_method(self, request, **values):
        example = {
                   "name": "Updated resource with id: %s." % (values['id']), 
                   "status": 200,
                   "requested_at": str(datetime.datetime.now()),
                   "body": json.dumps(request.form)
                   }
        
        return Response(json.dumps(example))
        