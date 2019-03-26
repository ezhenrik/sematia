import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from config import VENV_PATH

sys.path.append(VENV_PATH + '/lib/python3.7/site-packages')

from sematia import app

application = app.app

if __name__ == '__main__':
    application.run(threaded=True)
