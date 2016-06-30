from flask import Blueprint, make_response, render_template

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
            plaintext = plaintext
            r = make_response(render_template('pages/annotate.xml', plaintext=plaintext))
            r.headers.set('Access-Control-Allow-Origin', 'http://www.perseids.org')
            r.headers.set('Content-Type', 'application/xml; charset=utf-8')
            return r
        else:
            return ''
    else:
        return ''