from datetime import datetime
import traceback

import io

from flask import Blueprint, render_template, session, jsonify, redirect, \
                  url_for, request, send_file

from ..controllers import document, hand, layertreebank, message, \
                          user, userdocument

tools = Blueprint('tools', __name__, static_folder='/static')
Layertreebank = layertreebank.Layertreebank

def export(target):
    return send_file(Layertreebank.export(target), attachment_filename='treebanks-'+target+'.zip', as_attachment=True)

@tools.route('/')
def index():
    return render_template('pages/tools.html')

@tools.route('/export_all_treebanks', methods=['GET'])
def export_all_treebanks():
    return export('all')

@tools.route('/export_standard_treebanks', methods=['GET'])
def export_standard_treebanks():
    return export('standard')

@tools.route('/export_original_treebanks', methods=['GET'])
def export_original_treebanks():
    return export('original')

@tools.route('/find', methods=['POST'])
def find():
    query = {}
    options = {}
    options['document_title'] = request.form.get('document_title')
    options['document_title_mode'] = request.form.get('document_title_mode')
    options['document_provenience'] = request.form.get('document_provenience')
    options['document_provenience_mode'] = request.form.get('document_provenience_mode')
    options['document_date_not_before'] = request.form.get('document_date_not_before')
    options['document_date_not_after'] = request.form.get('document_date_not_after')
    options['hand_handwriting'] = request.form.getlist('hand_handwriting[]')
    options['hand_text_type'] = request.form.getlist('hand_text_type[]')
    query['original'] = {
        'q': request.form.get('original'),
        'plain': request.form.get('original_plain'),
        'mode': request.form.get('original_mode'),
        'relation': request.form.get('original_relation'),
        'relation_mode': request.form.get('original_relation_mode'),
        'postag': request.form.get('original_postag'),
        'postag_mode': request.form.get('original_postag_mode'),

    }
    query['standard'] = {
        'q': request.form.get('standard'),
        'plain': request.form.get('standard_plain'),
        'mode': request.form.get('standard_mode'),
        'relation': request.form.get('standard_relation'),
        'relation_mode': request.form.get('standard_relation_mode'),
        'postag': request.form.get('standard_postag'),
        'postag_mode': request.form.get('standard_postag_mode'),
    }
   
    result = Layertreebank.search(query, options)

    return jsonify(result=result)