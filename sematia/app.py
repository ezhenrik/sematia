import os
import logging

from flask import Flask, redirect, request, session, url_for
from flask.ext.bootstrap import Bootstrap

from .models import db
from .views import documents, docs, edit, user, users

app = Flask(__name__)

app.config.from_object('config')

app.basedir = os.path.abspath(os.path.dirname(__file__))

app.register_blueprint(documents.documents, url_prefix='/documents')
app.register_blueprint(docs.docs, url_prefix='/docs')
app.register_blueprint(edit.edit, url_prefix='/edit')
app.register_blueprint(user.user, url_prefix='/user')
app.register_blueprint(users.users, url_prefix='/users')

# Configure logging
if app.config['LOG']:
    logging.basicConfig(filename=app.config['LOGFILE'], level=logging.DEBUG)

# Check user before each request
@app.before_request
def before_request():
    if ('user_id' not in session 
                or 'user_role' not in session 
                or 'user_name' not in session 
                or 'user_admin' not in session) and \
                request.endpoint not in ['user.index', 
                                         'user.tokensignin', 
                                         'user.logout'] and \
                '/static/' not in request.path:
        session.clear()
        return redirect(url_for('user.index'))

@app.route('/')
def index():
    return redirect(url_for('documents.index'))

# Jinja2 extensions
def convertNoneToEmptyString(s):
    if s is None:
        return ''
    return s

app.jinja_env.globals.update(xstr=convertNoneToEmptyString)

Bootstrap(app)
db.init_app(app)