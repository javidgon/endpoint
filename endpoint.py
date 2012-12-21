import os
import redis
import urlparse
import requests
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
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
        
        def _is_valid_url(url):
            parts = urlparse.urlparse(url)
            return parts.scheme in ('http','https')
        
        error = None
        url = ''
        if request.method == 'POST':
            url = request.form['url']
            if not _is_valid_url(url):
                error = 'Please enter a valid URL'
                return self.render_template('index.html', error=error, url=url, resp='')
            else:
                return self.lets_perform_api_call(request)
        else:
            return self.render_template('index.html', error=error, url=url, resp='')
    
    
    def lets_perform_api_call(self, request):
        
        def get_or_create(api_call):
            known_api_call = self.redis.get(api_call)
            if known_api_call:
                return known_api_call
            else:
                req = requests.get(api_call)
                self.redis.setex(api_call, req.json(), 60*5)
                return self.redis.get(api_call)
        
        api_call = request.form['url']
        self.redis.incr('searches-count:' + api_call)
        resp = get_or_create(api_call)
            
        return self.render_template('index.html', error='', url=api_call, resp=resp)
        
    
def create_app(redis_host='localhost', redis_port=6379, with_static=True):
    # Set EndPoint object.
    app = EndPoint({
          'redis_host': redis_host,
          'redis_port': redis_port
    })
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static':  os.path.join(os.path.dirname(__file__), 'static')
    })
    return app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)