import os
from werkzeug.wsgi import SharedDataMiddleware

from endpoint import EndPoint
from readers.yaml_reader import YamlReader

def create_app(redis_host='localhost', redis_port=6379,
               with_static=True, test_mode=False):
    reader = YamlReader('endpoint.yaml')
    # Set EndPoint object.
    app = EndPoint({
          'redis_host': redis_host,
          'redis_port': redis_port,
          'test_mode': test_mode
    }, reader)
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static':  os.path.join(os.path.dirname(__file__), 'static')
    })
    return app

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)