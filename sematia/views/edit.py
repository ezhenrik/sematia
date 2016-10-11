from datetime import datetime
import traceback
import requests

from .. import app

from flask import Blueprint, render_template, session, jsonify, redirect, \
                  url_for, request

from ..controllers import document, hand, layertreebank, message, user, \
                          userdocument

from ..utils import log

Document = document.Document
Hand = hand.Hand
Layertreebank = layertreebank.Layertreebank
Message = message.Message
User = user.User
Userdocument = userdocument.Userdocument
Log = log.Log

edit = Blueprint('edit', __name__, static_folder='/static')

@edit.route('/<int:id>')
def index(id):
    layertreebank = Layertreebank.get(id)
    if layertreebank:
        hand = layertreebank.hand
        document = hand.document
        my = Userdocument.get_editable(document.id, session['user_id'])
        my_messages = Message.get_my()
        return render_template('pages/edit.html', ltb=layertreebank, 
                                doc=document, my=my, hand=hand, 
                                my_messages=my_messages)
    else:
        return redirect(url_for('documents.index'))

@edit.route('/add_treebank', methods=['POST'])
def add_treebank():
    id = request.form.get('id')
    file = request.files['file']
    return jsonify(Layertreebank.add_treebank(id, file))

@edit.route('/save_paths', methods=['POST'])
def save_paths():
    settings = request.form.get('paths').strip()
    id = request.form.get('id');
    return jsonify(Layertreebank.update_settings(id, settings))

@edit.route('/get_treebank', methods=['POST'])
def get_treebank():
    id = request.form.get('id').strip()
    return jsonify(Layertreebank.get_treebank(id))

@edit.route('/delete_treebank', methods=['POST'])
def delete_treebank():
    id = request.form.get('id').strip()
    return jsonify(Layertreebank.delete_treebank(id))

@edit.route('/store_plaintext', methods=['POST'])
def store_plaintext():
    id = request.form.get('id').strip()
    text = request.form.get('text').strip()
    return jsonify(Layertreebank.store_plaintext(id, text))

@edit.route('/post_treebank',  methods=['POST'])
def post_treebank():
    xml = request.form.get('xml').strip().encode('utf-8')
    if ('perseids' in session):
        access_token = session['perseids']

        url = 'https://sosol.perseids.org/sosol/api/v1/xmlitems/TreebankCite'
        headers = {
            'Content-Type': 'application/xml; charset=UTF-8',
            'Accept': 'application/json',
            'Authorization': 'Bearer '+access_token
        }
        r = requests.post(url, headers=headers, data=xml)
        r_json = r.json()
        if ('publication_id' in r_json):
            pubid = str(r_json['publication_id'])

            url = 'https://sosol.perseids.org/sosol/api/v1/publications/'+pubid
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Bearer '+access_token
            }
            data = {
                'community_name': app.app.config['PERSEIDS_COMMUNITY_NAME']
            }
            r = requests.put(url, headers=headers, data=data)
            Log.p(r.status_code)
            Log.p(r.text)
            Log.p(app.app.config['PERSEIDS_COMMUNITY_NAME'])
            if (r.status_code == '200'):
                return 'ok'
    return 'false'