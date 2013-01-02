# Small script that runs the mock server and nosetests at
# the same time. Useful for Travis or any other CI service.
from __future__ import with_statement
from fabric.api import local, abort, lcd
import os
import time
import requests
import sys
import glob

PATH = os.path.abspath(os.path.dirname(__file__))

def add_to_PYTHONPATH():
    print "Checking if endpoint/ is already in the PYTHONPATH..."
    python_bin = os.path.dirname(sys.executable)
    python_lib = os.path.join(python_bin, '..', 'lib/')
    python_version = glob.glob(os.path.join(python_lib + 'python*'))
    python_site_packages = os.path.join(python_version[0], 'site-packages/')

    if not os.path.exists(os.path.join(python_site_packages, 'endpoint.pth')):
        print "Adding endpoint/ to the PYTHONPATH..."
        with lcd(os.path.join(python_site_packages)):
            local('touch endpoint.pth')
            local('echo "%s" >> endpoint.pth' % os.path.join(PATH, '..'))
    else:
        print "It's already there. No changes have been applied." 
        

def test_suite():
    """
    Run the ENDPOINT application's tests suite.
    """
    with lcd(PATH):
        local("python run_mock.py &")
        time.sleep(3)
        local("nosetests")
        local("pkill -n python run_mock.py")
    
def supervise(yml_file="", mode='one_time', interval=60, test_mode=False):
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
    
    if not os.path.exists(os.path.join(PATH, yml_file)):
        abort("YML file not found.")
    try:
        interval = int(interval)
    except ValueError:
        abort("Interval parameter is not a number.")
    
    with lcd(PATH):
        print "Running server..."
        local("python run_app.py %s &" % yml_file)
        time.sleep(3)
        if test_mode:
            print "Running mock server..."
            local("python run_mock.py &")
            time.sleep(3)
        if mode == 'one_time':
            _process_response(yml_file, successes, errors)
            _print_output(successes, errors)
        elif mode =='strict':
            counter = 0
            while True:
                _process_response(yml_file, successes, errors)
                _print_output(successes, errors)
                print "Next check will be in %d seconds. This is the attempt %d." % (interval, counter)
                counter += 1
                successes, errors = [],[]
                time.sleep(interval)
        else:
            abort("Sorry but this mode is not currently supported.")
        print "Stopping server..."
        local("killall python run_app.py")
    
def _process_response(yml_file, successes, errors):
    from endpoint.settings import SERVER
    print "Making the requests..."
    response = requests.get("http://%s:%s/" % 
                              (SERVER['host'], SERVER['port']))
    
    for endpoint in response.json():
        if endpoint['tests_passed'] == False:
            errors.append(endpoint)
        elif endpoint['tests_passed'] == True:
            successes.append(endpoint)

def _print_output(successes, errors):
    if len(errors) == 0:
        print "Congrats, the endpoints work fine."
    else:
        print "Sorry but we encountered some problems in the endpoints."
        print "%s" % str(errors)
        
    print " # Results: %d successes and %d errors" % (len(successes), len(errors))
