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