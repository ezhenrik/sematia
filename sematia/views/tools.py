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

def export_words(target):
    return send_file(Layertreebank.export_words(target), attachment_filename='words-'+target+'.zip', as_attachment=True)

def hierarchical_clustering(target):
    return send_file(Layertreebank.get_hierarchy(target), mimetype='image/png')


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

@tools.route('/export_all_words', methods=['GET'])
def export_all_words():
    return export_words('all')

@tools.route('/export_standard_words', methods=['GET'])
def export_standard_words():
    return export_words('standard')

@tools.route('/export_original_words', methods=['GET'])
def export_original_words():
    return export_words('original')

@tools.route('/find', methods=['GET'])
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
    options['hand_addressee'] = request.form.getlist('hand_addressee[]')
    options['actual_writer_tmid'] = request.form.get('actual_writer_tmid')
    options['scribal_official_tmid'] = request.form.get('scribal_official_tmid')
    options['author_tmid'] = request.form.get('author_tmid')
    options['addressee_tmid'] = request.form.get('addressee_tmid')
    query['original'] = {
        'q': request.form.get('original'),
        'plain': request.form.get('original_plain'),
        'lemma': request.form.get('original_lemma'),
        'lemma_plain': request.form.get('original_lemma_plain'),
        'relation': request.form.get('original_relation'),
        'postag': request.form.get('original_postag'),

    }
    query['standard'] = {
        'q': request.form.get('standard'),
        'plain': request.form.get('standard_plain'),
        'lemma': request.form.get('standard_lemma'),
        'lemma_plain': request.form.get('standard_lemma_plain'),
        'relation': request.form.get('standard_relation'),
        'postag': request.form.get('standard_postag'),
    }
   
    result = Layertreebank.search(query, options)

    return jsonify(result=result)

@tools.route('/hierarchy_all', methods=['GET'])
def hierarchy_all():
    return hierarchical_clustering('all')

@tools.route('/hierarchy_standard', methods=['GET'])
def hierarchy_standard():
    return hierarchical_clustering('standard')

@tools.route('/hierarchy_original', methods=['GET'])
def hierarchy_original():
    return hierarchical_clustering('original')
