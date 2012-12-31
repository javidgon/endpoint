import sys

from endpoint.sentinel import Sentinel
from endpoint.readers.yaml_reader import YamlReader
from endpoint.settings import TESTING_YML_PATH

def create_app(test_mode=True, yalm_file=None):
    reader = YamlReader(yalm_file)
    sentinel = Sentinel({
          'test_mode': test_mode
    }, reader)

    return sentinel

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    from endpoint.settings import SERVER
    # Default yaml file if no params are passed.
    yalm_file = TESTING_YML_PATH
    if len(sys.argv) > 1:
        yalm_file = sys.argv[1]

    app = create_app(yalm_file=yalm_file)
    run_simple(SERVER['host'], SERVER['port'], app, use_debugger=True, use_reloader=True)