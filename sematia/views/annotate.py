from flask import Blueprint, Response, render_template

from .. import app

from ..controllers import layertreebank

annotate = Blueprint('annotate', __name__, static_folder='/static')

Layertreebank = layertreebank.Layertreebank

@annotate.route('/<int:id>')
def index(id):
    layertreebank = Layertreebank.get(id)
    if layertreebank:
        plaintext = layertreebank.plaintext
        if plaintext:
            resp = Response()
            resp.headers['Access-Control-Allow-Origin'] = 'http://www.perseids.org'
            resp.headers['Content-Type'] = 'text/html; charset=utf-8'
            return render_template('pages/annotate.txt', plaintext=plaintext)
        else:
            return ''
    else:
        return ''