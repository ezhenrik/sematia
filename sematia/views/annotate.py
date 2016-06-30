from flask import Blueprint, Response

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
            resp = Response(plaintext)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Content-Type'] = 'text/plain'
            return resp
        else:
            return ''
    else:
        return ''