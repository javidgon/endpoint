import os

# Development and mock server configs
SERVER = {"host": "127.0.0.1", "port": 5000}
MOCK_SERVER = {"host": "127.0.0.1", "port": 5100}

# SMTP settings.
SMTP_SERVER = smtplib.SMTP('smtp.gmail.com',587) #port 465 or 587
SMTP_LOGIN = ''
SMTP_PASSWORD = ''
SMTP_FROM = ''
SMTP_TO = ''
SMTP_MSG = ''
SMTP_STATUS = False

# TESTING YML PATH
SPECS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'specs'))

