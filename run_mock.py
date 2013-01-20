from endpoint.tests.mock import Mock

def create_mock():
    # Create Mock
    return Mock()

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    from endpoint.settings import MOCK_SERVER
    # Just for Development. Use WSGI instead in Production.
    run_simple(MOCK_SERVER['host'], MOCK_SERVER['port'], create_mock(), use_debugger=True, use_reloader=True)