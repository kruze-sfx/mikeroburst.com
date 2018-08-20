import os
import sys

try:
    from config import interp
except ImportError:
    raise ValueError("Must define interp in a local file named config.py")

if sys.executable != interp:
    os.execl(interp, interp, *sys.argv)
sys.path.append(os.getcwd())

from url_handler import app as application  # noqa

_ = application  # silence pep8

# Passenger requrires a passenger_wsgi.py file and looks for a callable in it
# called application. Passenger uses application to serve requests.
# In this case, all of the URL handling logic is implemented in url_handler.py
# so we just import application from there.
