from datetime import datetime
import traceback

from flask import Blueprint, render_template, session, jsonify, redirect, \
                  url_for, request

from ..controllers import document, hand, layertreebank, message, \
                          user, userdocument

documents = Blueprint('documents', __name__, static_folder='/static')

Document = document.Document
Hand = hand.Hand
Layertreebank = layertreebank.Layertreebank
Message = message.Message
User = user.User
Userdocument = userdocument.Userdocument

@documents.route('/')
def index():
    documents = Document.get_all()
    my_messages = Message.get_my()
    return render_template('pages/documents.html', documents=documents, 
                            my_messages=my_messages,
                            user_id=session['user_id'], 
                            admin=session['user_admin'], 
                            user_role=session['user_role']
                          )

@documents.route('/add_document', methods=['POST'])
def add_document():
    url = request.form.get('url').strip()
    return jsonify(Document.add(url))

@documents.route('/edit_document', methods=['POST'])
def edit_document():
    id = request.form.get('id').strip()
    meta_date_not_before = request.form.get('meta_date_not_before').strip()
    meta_date_not_after = request.form.get('meta_date_not_after').strip()
    meta_provenience = request.form.get('meta_provenience').strip()
    meta_title = request.form.get('meta_title').strip()
    return jsonify(Document.edit(id, meta_title, meta_date_not_before, 
                                 meta_date_not_after, meta_provenience))

@documents.route('/delete_document', methods=['POST'])
def delete_document():
    id = request.form.get('id');
    return jsonify(Document.delete(id))

@documents.route('/get_hands', methods=['POST'])
def get_hands():
    my = request.form.get('my').strip()
    document_id = request.form.get('id').strip()
    hands = Hand.get_all(document_id)
    return render_template('pages/hand-table.html', hands=hands, my=my)

@documents.route('/edit_hand', methods=['POST'])
def edit_hand():
    id = request.form.get('id').strip()
    meta_handwriting_description_edition = request.form \
        .get('meta_handwriting_description_edition').strip()
    meta_handwriting_description_custom = request.form \
        .get('meta_handwriting_description_custom').strip()
    meta_handwriting_professional = request.form \
        .get('meta_handwriting_professional').strip()
    meta_handwriting_same_hand = request.form \
        .get('meta_handwriting_same_hand').strip()
    meta_writer_name = request.form \
        .get('meta_writer_name').strip()
    meta_writer_title = request.form \
        .get('meta_writer_title').strip()
    meta_scribal_name = request.form \
        .get('meta_scribal_name').strip()
    meta_scribal_title = request.form \
        .get('meta_scribal_title').strip()
    meta_author_name = request.form \
        .get('meta_author_name').strip()
    meta_author_title = request.form \
        .get('meta_author_title').strip()
    meta_text_type = request.form \
        .get('meta_text_type').strip()
    meta_addressee = request.form \
        .get('meta_addressee').strip()
    meta_addressee_name = request.form \
        .get('meta_addressee_name').strip()
    meta_addressee_title = request.form \
        .get('meta_addressee_title').strip()

    return jsonify(Hand.edit(
        id,
        meta_handwriting_description_edition,
        meta_handwriting_description_custom,
        meta_handwriting_professional,
        meta_handwriting_same_hand,
        meta_writer_name,
        meta_writer_title,
        meta_scribal_name,
        meta_scribal_title,
        meta_author_name,
        meta_author_title,
        meta_text_type,
        meta_addressee,
        meta_addressee_name,
        meta_addressee_title
    ))

@documents.route('/get_treebank', methods=['POST'])
def get_treebank():
    id = request.form.get('id').strip()
    return jsonify(Layertreebank.get_treebank(id))

@documents.route('/update_treebank', methods=['POST'])
def update_treebank():
    id = request.form.get('id').strip()
    status = request.form.get('status').strip()
    return jsonify(Layertreebank.update_treebank(id, status))

@documents.route('/get_contributors', methods=['POST'])
def get_contributors():
    ids = request.form.getlist('ids[]')
    return jsonify(User.get_contributors(ids))

@documents.route('/add_contributor', methods=['POST'])
def add_contributor():
    id = request.form.get('id').strip()
    document_id = request.form.get('document_id').strip()
    return jsonify(Userdocument.add(id, document_id))

@documents.route('/remove_contributor', methods=['POST'])
def remove_contributor():
    id = request.form.get('id').strip()
    document_id = request.form.get('document_id').strip()
    return jsonify(Userdocument.delete(id, document_id))

@documents.route('/get_messages', methods=['POST'])
def get_messages():
    id = request.form.get('id')
    return jsonify(Message.get_document_messages(id))

@documents.route('/add_message', methods=['POST'])
def add_message():
    id = request.form.get('id')
    body = request.form.get('body')
    return jsonify(Message.add(id, body))

@documents.route('/delete_message', methods=['POST'])
def delete_message():
    id = request.form.get('id')
    return jsonify(Message.delete(id))