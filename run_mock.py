from tests.mock import Mock

def create_mock():
    # Create Mock
    return Mock()

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    mock = create_mock()
    run_simple('127.0.0.1', 5100, mock, use_debugger=True, use_reloader=True)