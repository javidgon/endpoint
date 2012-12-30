import sys

from endpoint.sentinel import Sentinel
from endpoint.run_mock import create_mock
from endpoint.readers.yaml_reader import YamlReader
from endpoint.settings import TESTING_YAML_PATH

def create_app(test_mode=True, yalm_file=None):
    reader = YamlReader(yalm_file)
    sentinel = Sentinel({
          'test_mode': test_mode
    }, reader)

    return sentinel

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    # Default yaml file if no params are passed.
    yalm_file = TESTING_YAML_PATH
    if len(sys.argv) > 1:
        yalm_file = sys.argv[1]

    app = create_app(yalm_file=yalm_file)
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)