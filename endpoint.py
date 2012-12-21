import os
import redis
import urlparse
import requests
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader

class EndPoint(object):
    def __init__(self, config):
        self.redis = redis.Redis(config['redis_host'], config['redis_port'])
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                     autoescape=True)
        self.url_map = Map([
            Rule('/', endpoint='search')                
        ])
        
    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')
    
    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'lets_' + endpoint)(request, **values)
        except HTTPException, e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)
    
    # Make the app actually 'callable'
    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
    
    # Views.
    def lets_search(self, request, **values):
        
        def _is_valid_url(api_call):
            parts = urlparse.urlparse(api_call)
            return parts.scheme in ('http','https')

        context = {'error': None, 'api_call':'', 'resp': None, 'redis': None}
        if request.method == 'POST':
            context['api_call'] = request.form['api-call']
            if _is_valid_url(context['api_call']):
                context['resp'], context['redis'] = self.lets_perform_api_call(request)
            else:
                context['error'] = 'Please enter a valid URL'
        return self.render_template('index.html', **context)
    
    
    def lets_perform_api_call(self, request):
        
        def _get_or_create(api_call):
            known_api_call = self.redis.get(api_call)
            if known_api_call:
                return known_api_call, True
            else:
                req = requests.get(api_call)
                self.redis.setex(api_call, req.json(), 60*5)
                return self.redis.get(api_call), False

        api_call = request.form['api-call']
        self.redis.incr('searches-count:' + api_call)
        
        return _get_or_create(api_call)
        