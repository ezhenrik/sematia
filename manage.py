import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from config import VENV_PATH

sys.path.append(VENV_PATH + '/lib/python3.5/site-packages')

from sematia.app import app
from sematia.models import db

from flask.ext.script import Manager
from flask.ext.migrate import Migrate
from flask.ext.migrate import MigrateCommand

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

app.debug = True
manager.run() 