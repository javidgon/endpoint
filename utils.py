from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException
from settings import (JINJA_ENV,SMTP_SERVER,
                      SMTP_LOGIN, SMTP_PASSWORD, SMTP_FROM,
                      SMTP_TO, SMTP_MSG)
    
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

def send_notification():
    server = SMTP_SERVER
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(SMTP_LOGIN, SMTP_PASSWORD)
    server.sendmail(SMTP_FROM, SMTP_TO, SMTP_MSG)
    server.close()

    return 'Error notification sent successfully'