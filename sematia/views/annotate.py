from flask import Blueprint

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
            return return plaintext, 200, {'Content-Type': 'text/css; charset=utf-8'}
        else:
            return ''
    else:
        return ''