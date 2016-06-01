from flask import Blueprint, send_from_directory

from .. import app

docs = Blueprint('docs', __name__, static_folder='/docs')

# Documentation

@docs.route('/', defaults={'filename': 'index.html'}, strict_slashes=True)
@docs.route('/<path:filename>')
def documentation(filename):
    return send_from_directory(app.app.basedir + '/static/docs/_build/html', filename)
