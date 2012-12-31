# Small script that runs the mock server and nosetests at
# the same time. Useful for Travis or any other CI service.
from fabric.api import local

def run_tests():
    local("python run_mock.py &")
    local("nosetests")