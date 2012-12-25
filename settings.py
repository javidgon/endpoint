import os
from jinja2 import Environment, FileSystemLoader

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__),
                                    'templates')
JINJA_ENV = Environment(loader=FileSystemLoader(TEMPLATE_PATH),
                                     autoescape=True)