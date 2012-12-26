import json

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from utils import dispatch_request

class Mock(object):
    def __init__(self):
        self.url_map = Map([
            Rule('/mock/', endpoint='get_method'),
            Rule('/mock/post', endpoint='post_method'),
            Rule('/mock/put/<int:id>', endpoint='put_method')
        ])

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = dispatch_request(self, request)

        return response(environ, start_response)

    def get_method(self, request, **values):
        example = {
                   "name": "This is a JSON obj created just for the GET method.", 
                   "status": 200
                   }

        return Response(json.dumps(example))
    
    def post_method(self, request, **values):
        example = {
                   "name": "Created new resource.", 
                   "status": 200,
                   "body": json.dumps(request.form)
                   }
        
        return Response(json.dumps(example))
    
    def put_method(self, request, **values):
        example = {
                   "name": "Updated resource with id: %s." % (values['id']), 
                   "status": 200,
                   "body": json.dumps(request.form)
                   }
        
        return Response(json.dumps(example))
        