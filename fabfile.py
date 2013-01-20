# Small script that runs the mock server and nosetests at
# the same time. Useful for Travis or any other CI service.
from __future__ import with_statement
from fabric.api import local, abort, cd
from endpoint.settings import SERVER
import os
import time
import requests
import sys

PATH = os.path.abspath(os.path.dirname(__file__))

def test_suite():
    """
    Run the ENDPOINT application's tests suite.
    """
    sys.path.append(os.path.join(PATH,'..'))
    with cd(PATH):
        local("python run_mock.py &")
        time.sleep(3)
        local("nosetests")
        local("pkill -n python run_mock.py")
    
def supervise(yml_file="", mode='one_time', route='tests', interval=60, test_mode=False):
    """
    Supervise endpoints and inform in case of any problem.
    There're two modes availables:
        - one_time: Check the endpoints just a single time.
        - strict: Check the endpoints every <interval> seconds.
    Also, there's a special "mock" option which will simulate a server
    with several predefined endpoints.
    """
    successes = []
    errors = []
    
    sys.path.append(os.path.join(PATH,'..'))
    if not os.path.exists(os.path.join(PATH, yml_file)):
        abort("YML file not found.")
    try:
        interval = int(interval)
    except ValueError:
        abort("Interval parameter is not a number.")
    
    with cd(PATH):
        print "Running server..."
        local("python run_server.py %s &" % yml_file)
        time.sleep(3)
        if test_mode:
            print "Running mock server..."
            local("python run_mock.py &")
            time.sleep(3)
        if mode == 'one_time':
            if _process_response(yml_file, route, successes, errors):
                _print_output(successes, errors)
        elif mode =='strict':
            counter = 0
            while True:
                if _process_response(yml_file, route, successes, errors):
                    _print_output(successes, errors)
                print "Next check will be in %d seconds. This is the attempt %d." % (interval, counter)
                counter += 1
                successes, errors = [],[]
                time.sleep(interval)
        else:
            abort("Sorry but this mode is not currently supported.")
        print "Stopping server..."
        local("killall python run_server.py")
    
def _process_response(yml_file, route, successes, errors):
    print "Making the requests..."
    response = requests.get("http://%s:%s/%s" % 
                              (SERVER['host'], SERVER['port'], route))

    if response.text == '[]' or response.text == '{}':
        print "Empty response. Are you sure that the specification file exists?"
        return False
    else:
        if isinstance(response.json(), list):
            for endpoint in response.json():
                if endpoint['tests_passed'] == False:
                    errors.append(endpoint)
                elif endpoint['tests_passed'] == True:
                    successes.append(endpoint)
        else:
            if response.json()['tests_passed'] == False:
                errors.append(response.json())
            else:
                successes.append(response.json())
        return True

def _print_output(successes, errors):
    if len(errors) == 0:
        print "Congrats, the endpoints work fine."
    else:
        print "Sorry but we encountered some problems in the endpoints."
        print "%s" % str(errors)
        
    print " # Results: %d successes and %d errors" % (len(successes), len(errors))
