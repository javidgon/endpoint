import requests
import json
import datetime
from collections import OrderedDict
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException
from endpoint.settings.settings import (JINJA_ENV,SMTP_SERVER,
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
    except HTTPException as e:
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

def make_request_with_auth(url, method, auth, user, password, data=None):
    # GET
    if method== 'GET' and auth == "basic":
        return requests.get(url, auth=HTTPBasicAuth(user, password))
    elif method == 'GET' and auth == "digest":
        return requests.get(url, auth=HTTPDigestAuth(user, password))
    
    # POST
    if method == 'POST' and auth == "basic":
        return requests.post(url, data, auth=HTTPBasicAuth(user, password))
    elif method == 'POST' and auth == "digest":
        return requests.post(url, data, auth=HTTPDigestAuth(user, password))
    
    #PUT
    if method == 'PUT' and auth == "basic":
        return requests.put(url, data=json.dumps(data), auth=HTTPBasicAuth(user, password))
    elif method == 'PUT' and auth == "digest":
        return requests.put(url, data=json.dumps(data), auth=HTTPDigestAuth(user, password))
    
    raise NotImplemented('HTTP Method or Auth not recognized')

def make_request_without_auth(url, method, data=None):
    if method == 'GET':
        return requests.get(url)
    elif method == 'POST':
        return requests.post(url, data)
    elif method == 'PUT':
        return requests.put(url, data=json.dumps(data))
    
    raise NotImplemented('HTTP Method not recognized')

def make_request(endpoint):
        url = endpoint['url']
        method = endpoint['method']
        data = endpoint['config']['request-body']
        auth_method = endpoint['auth']['type']
        
        if auth_method:
            user = endpoint['auth']['user']
            password = endpoint['auth']['pass']
            
        if auth_method:
            return make_request_with_auth(url, method, auth_method, user, password, data)
        else:
            return make_request_without_auth(url, method, data)
        
def build_response(response, tests_passed=False):
    json_resp = OrderedDict([
            ("status_code", response.status_code),
            ("url", response.url),
            ("method", response.request.method),
            ("tests_passed", tests_passed),
            ("requested_at", str(datetime.datetime.now())), 
            ])
    
    return json_resp

def render_http_error(error, resp_status_code, assert_status_code):
    if error == 'SERVER_UNREACHABLE':
        return OrderedDict([
                                  ("status_code", resp_status_code),
                                  ("log", "Server unreachable"),
                                  ("tests_passed", resp_status_code == assert_status_code),
                                  ("requested_at", str(datetime.datetime.now()))
                                  ])
    elif error == 'INVALID_URL':
        return OrderedDict([
                                  ("status_code", resp_status_code),
                                  ("log", "Invalid URL"),
                                  ("tests_passed", resp_status_code == assert_status_code),
                                  ("requested_at", str(datetime.datetime.now()))
                                  ])
    else:
        raise NotImplemented
