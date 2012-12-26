import os
import smtplib
from jinja2 import Environment, FileSystemLoader

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__),
                                    'templates')
JINJA_ENV = Environment(loader=FileSystemLoader(TEMPLATE_PATH),
                                     autoescape=True)
# SMTP settings.
SMTP_SERVER = smtplib.SMTP('smtp.gmail.com',587) #port 465 or 587
SMTP_LOGIN = ''
SMTP_PASSWORD = ''
SMTP_FROM = ''
SMTP_TO = ''
SMTP_MSG = ''
SMTP_STATUS = False

# Predefined blocks.
SERVER_UNREACHABLE = {
                      "status": 404,
                      "log": "Server unreachable"
                      }
