import os
import sys

INTERP = os.path.join(os.environ['HOME'], 'preview.mikeroburst.com', 'venv', 'bin', 'python')  # noqa
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())

from url_handler import app as application  # noqa

_ = application  # silence pep8

# Passenger requrires a passenger_wsgi.py file and looks for a callable in it
# called application. Passenger uses application to serve requests.
# In this case, all of the URL handling logic is implemented in url_handler.py
# so we just import application from there.
