from endpoint.sentinel import Sentinel

def application():
    sentinel = Sentinel()

    return sentinel

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    from endpoint.settings import SERVER
    
    # Just for Development. Use WSGI instead in Production.
    run_simple(SERVER['host'], SERVER['port'], application(), use_debugger=True, use_reloader=True)