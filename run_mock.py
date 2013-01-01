from endpoint.tests.mock import Mock
from endpoint.settings import MOCK_SERVER

def create_mock():
    # Create Mock
    return Mock()

if __name__ == '__main__':
    from werkzeug.serving import run_simple

    mock = create_mock()
    run_simple(MOCK_SERVER['host'], MOCK_SERVER['port'], mock, use_debugger=True, use_reloader=True)