import requests
import json
import datetime
from collections import OrderedDict
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from werkzeug.exceptions import HTTPException, NotImplemented
from endpoint.settings import (SMTP_SERVER,
                      SMTP_LOGIN, SMTP_PASSWORD, SMTP_FROM,
                      SMTP_TO, SMTP_MSG)

def dispatch_request(obj, request):
    adapter = obj.url_map.bind_to_environ(request.environ)
    try:
        endpoint, values = adapter.match()
        return getattr(obj, endpoint)(request, **values)
    except HTTPException as e:
        return e

def send_notification():
    """
    Send email in case of problem. SMTP_STATUS must be TRUE.
    """
    server = SMTP_SERVER
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(SMTP_LOGIN, SMTP_PASSWORD)
    server.sendmail(SMTP_FROM, SMTP_TO, SMTP_MSG)
    server.close()

    return 'Error notification sent successfully'

def make_request_with_auth(url, method, auth, user, password, data=None, timeout=10.0):
    """
    Make request if it requires AUTH. Basic and Digest supported so far.
    """
    # GET
    if method== 'GET' and auth == "basic":
        return requests.get(url, auth=HTTPBasicAuth(user, password), timeout=timeout)
    elif method == 'GET' and auth == "digest":
        return requests.get(url, auth=HTTPDigestAuth(user, password), timeout=timeout)
    
    # POST
    if method == 'POST' and auth == "basic":
        return requests.post(url, data, auth=HTTPBasicAuth(user, password), timeout=timeout)
    elif method == 'POST' and auth == "digest":
        return requests.post(url, data, auth=HTTPDigestAuth(user, password), timeout=timeout)
    
    #PUT
    if method == 'PUT' and auth == "basic":
        return requests.put(url, data=json.dumps(data), auth=HTTPBasicAuth(user, password), timeout=timeout)
    elif method == 'PUT' and auth == "digest":
        return requests.put(url, data=json.dumps(data), auth=HTTPDigestAuth(user, password), timeout=timeout)
    
    raise NotImplemented('HTTP Method or Auth not recognized')

def make_request_without_auth(url, method, data=None, timeout=10.0):
    """
    Make request if it doesn't require AUTH.
    """
    if method == 'GET':
        return requests.get(url, timeout=timeout)
    elif method == 'POST':
        return requests.post(url, data, timeout=timeout)
    elif method == 'PUT':
        return requests.put(url, data=json.dumps(data), timeout=timeout)
    
    raise NotImplemented('HTTP Method not recognized')

def make_request(endpoint):
    """
    Entry point of the making requests methods' ecosystem.
    """
    url = endpoint['url']
    method = endpoint['method']
    data = endpoint['config']['request-body']
    auth_method = endpoint['auth']['type']
    timeout = endpoint['asserts']['waiting-time'] if endpoint['asserts']['waiting-time'] else 10.0

    if auth_method:
        user = endpoint['auth']['user']
        password = endpoint['auth']['pass']
            
    if auth_method:
        return make_request_with_auth(url, method, auth_method, user, password, data, timeout)
    else:
        return make_request_without_auth(url, method, data, timeout)

def render_response(error=None, status_code=None, obj=None, response=None, tests_passed=False):
    """
    Build response based on the HTTP errors raised, the tests ran, and the specifications of each
    endpoint in the .yml file.
    """
    if error == 'SERVER_UNREACHABLE':
        return OrderedDict([
                                  ("status_code", status_code),
                                  ("log", error),
                                  ("tests_passed", status_code == obj['asserts']['status-code']),
                                  ("requested_at", str(datetime.datetime.now()))
                                  ])
    elif error == 'NOT_IMPLEMENTED':
        return OrderedDict([
                                  ("status_code", status_code),
                                  ("log", error),
                                  ("tests_passed", status_code == obj['asserts']['status-code']),
                                  ("requested_at", str(datetime.datetime.now()))
                                  ])
        
    elif error == 'REQUEST_TIMEOUT':
        return OrderedDict([
                                  ("status_code", status_code),
                                  ("log", error),
                                  ("tests_passed", status_code == obj['asserts']['status-code']),
                                  ("requested_at", str(datetime.datetime.now()))
                                  ])
    elif error == 'BAD_REQUEST':
        return OrderedDict([
                                  ("status_code", status_code),
                                  ("log", error),
                                  ("tests_passed", status_code == obj['asserts']['status-code']),
                                  ("requested_at", str(datetime.datetime.now()))
                                  ])
    else:
        return OrderedDict([
                                   ("status_code", response.status_code),
                                   ("url", response.url),
                                   ("method", response.request.method),
                                   ("tests_passed", tests_passed),
                                   ("requested_at", str(datetime.datetime.now())), 
                                   ])
