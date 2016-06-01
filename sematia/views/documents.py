from datetime import datetime
import traceback

from flask import Blueprint, render_template, session, jsonify, redirect, \
                  url_for, request

from ..controllers import documents
from ..utils import records

Documents = documents.Documents
Records = records.Records
documents = Blueprint('documents', __name__, static_folder='/static')

@documents.route('/')
def index():
    documents = Records.all('Document')
    user_role = session['user_role'] if 'user_role' in session else 0

    return render_template('pages/documents.html', documents=documents, 
                            user_id=session['user_id'], my=False, 
                            user_role=user_role)

@documents.route('/add_document', methods=['POST'])
def add_document():
    url = request.form.get('url').strip()
    return Documents.add_document(url)

@documents.route('/edit_document', methods=['POST'])
def edit_document():
    id = request.form.get('id').strip()
    meta_date_not_before = request.form.get('meta_date_not_before').strip()
    meta_date_not_after = request.form.get('meta_date_not_after').strip()
    meta_provenience = request.form.get('meta_provenience').strip()
    meta_title = request.form.get('meta_title').strip()
    return Documents.edit_document(id, meta_title, meta_date_not_before, meta_date_not_after, 
        meta_provenience)

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

    return Documents.edit_hand(
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
    )

@documents.route('/get_hands', methods=['POST'])
def get_hands():
    id = request.form.get('id').strip()
    my = request.form.get('my').strip()
    hands = Documents.get_hands(id)
    document = Records.get('Document', id)
    return render_template('pages/hand-table.html', hands=hands, my=my)

@documents.route('/get_contributors', methods=['POST'])
def get_contributors():
    contributors = []
    all_users = []
    ids = request.form.getlist('ids[]')
    users = Records.get('User', ids)
    for user in users:
        contributor = {
            'name': user.name,
            'id': user.id,
            'you': int(user.id == session['user_id'])
        }
        contributors.append(contributor)

    users = Records.all('User')
    for user in users:
        u = {
            'label': user.name,
            'value': user.id,
        }
        all_users.append(u)

    return jsonify({'contributors': contributors, 'all_users':all_users})

@documents.route('/remove_contributor', methods=['POST'])
def remove_contributor():
    id = request.form.get('id').strip()
    if id != session['user_id']:
        document_id = request.form.get('document_id').strip()
        return(Documents.remove_contributor(id, document_id))

@documents.route('/add_contributor', methods=['POST'])
def add_contributor():
    id = request.form.get('id').strip()
    document_id = request.form.get('document_id').strip()
    return(Documents.add_contributor(id, document_id))

@documents.route('/delete_document', methods=['POST'])
def delete_document():
    id = request.form.get('id');
    return Documents.delete_document(id)

@documents.route('/get_treebank', methods=['POST'])
def get_treebank():
    id = request.form.get('id').strip()
    return(Documents.get_treebank(id))

@documents.route('/update_treebank', methods=['POST'])
def update_treebank():
    id = request.form.get('id').strip()
    status = request.form.get('status').strip()
    return(Documents.update_treebank(id, status))