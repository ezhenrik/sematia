from datetime import datetime
import traceback

from flask import Blueprint, render_template, session, jsonify, redirect, \
                  url_for, request

from ..controllers import document, hand, layertreebank, user, \
                          userdocument

Document = document.Document
Hand = hand.Hand
Layertreebank = layertreebank.Layertreebank
User = user.User
Userdocument = userdocument.Userdocument

edit = Blueprint('edit', __name__, static_folder='/static')

@edit.route('/<int:id>')
def index(id):
    layertreebank = Layertreebank.get(id)
    if layertreebank:
        hand = layertreebank.hand
        document = hand.document
        my = Userdocument.get_editable(document.id, session['user_id'])
        return render_template('pages/edit.html', ltb=layertreebank, 
                                doc=document, my=my, hand=hand)
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