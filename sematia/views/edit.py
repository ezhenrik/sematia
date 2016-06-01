from datetime import datetime
import traceback

from flask import Blueprint, render_template, session, jsonify, redirect, \
                  url_for, request

from ..controllers import edit, documents
from ..utils import records, xml, log
from ..models import db, User, Document, Hand, Userdocument

Edit = edit.Edit
Documents = documents.Documents
Records = records.Records
Xml = xml.Xml
Log = log.Log
edit = Blueprint('edit', __name__, static_folder='/static')

@edit.route('/<int:id>')
def index(id):
    layer = Records.get('Layertreebank', id)
    if layer:
        hand = layer.hand
        document = hand.document

        my_document = Userdocument.query.filter_by(document_id=document.id, 
                    user_id=session['user_id']).first()
        return render_template('pages/edit.html', ltb=layer, 
                                doc=document, my=my_document, hand=hand)
    else:
        return redirect(url_for('documents.index'))

@edit.route('/add_treebank', methods=['POST'])
def add_treebank():
    try:
        id = request.form.get('id')
        layertreebank = Records.get('Layertreebank', id)
        data = {'status':'error', 'message': 'Could not upload the treebank'}
        if layertreebank:
            my_document = Userdocument.query.filter_by(
                document_id=layertreebank.hand.document.id, 
                    user_id=session['user_id']).first()
            if my_document:
                file = request.files['file']
                if '.' in file.filename and \
                        file.filename.rsplit('.', 1)[1] in ['xml', 'txt']:
                    contents = file.read().decode('utf-8')
                    if Xml.validate(contents):
                        layertreebank.body = contents
                        db.session.commit()
                        data = {'status':'ok', 'mode': 'added'}
                    else:
                        data = {'status':'error', 'message': 'Please validate the XML.'}
    except Exception:
        Log.e()
        return jsonify(data)
    return jsonify(data)

@edit.route('/save_paths', methods=['POST'])
def savepaths():
    settings = request.form.get('paths').strip()
    id = request.form.get('id');
    try:
        layertreebank = Records.get('Layertreebank', id)
        my_document = Userdocument.query.filter_by(
            document_id=layertreebank.hand.document.id, 
                user_id=session['user_id']).first()
        if layertreebank and my_document:
            layertreebank.settings = settings
            db.session.commit()
            data = {'status':'ok'}
    except Exception:
        return jsonify({'status':'error', 
                        'message': 'Could not retrieve the treebank.'})
    return jsonify(data)

@edit.route('/get_treebank', methods=['POST'])
def get_treebank():
    id = request.form.get('id').strip()
    return(Documents.get_treebank(id))

@edit.route('/delete_treebank', methods=['POST'])
def delete_treebank():
    id = request.form.get('id').strip()
    return(Documents.delete_treebank(id))