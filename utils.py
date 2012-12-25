from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException
from settings import JINJA_ENV
    
def render_template(template_name, obj):
    t = JINJA_ENV.get_template(template_name)
    return Response(t.render(obj), mimetype='text/html')

def dispatch_request(obj, request):
    adapter = obj.url_map.bind_to_environ(request.environ)
    try:
        endpoint, values = adapter.match()
        return getattr(obj, endpoint)(request, **values)
    except HTTPException, e:
        return e