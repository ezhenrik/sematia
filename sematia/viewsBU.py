from datetime import datetime
import json
import re
import traceback 

from app import app
from db import db
from flask import Flask, flash, render_template, request, jsonify, session, \
                  redirect, url_for, g, send_from_directory
from logging import Formatter, FileHandler
import requests

from models import Document, Hand, Layertreebank, User
from helpers import DbHelpers, XmlHelpers

# Jinja2 extensions

def convertNoneToEmptyString(s):
    if s is None:
        return ''
    return s

app.jinja_env.globals.update(xstr=convertNoneToEmptyString)

# Login system

@app.before_request
def before_request():
    if 'user_id' not in session \
        and request.endpoint != 'signin' \
        and request.endpoint != 'verify' \
        and request.endpoint != 'logout' \
        and '/static/' not in request.path \
        and '/docs/' not in request.path:
        return redirect(url_for('signin'))
    elif 'user_name' in session:
        g.user = session['user_name']

@app.route('/')
def index():
    return redirect(url_for('documents'))

@app.route('/signin')
def signin():
    if 'user_id' not in session:
        return render_template('pages/signin.html')
    else:
        return redirect(url_for('documents'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('signin'))

@app.route('/verify')
def verify():
    r = requests.get('https://www.googleapis.com/oauth2/v1/userinfo?access_token=' \
        +request.args.get('access_token'))
    j = json.loads(r.text)
    if j['verified_email']:
        user = User.query.filter_by(auth_id=j['id']).first()
        if user:
            user.name = j['name']
        else:
            user = User(j['name'], 1, j['id'], 'google')
            db.session.add(user)
        db.session.commit()

        session['user_name'] = j['name']
        session['user_id'] = user.id
        session['user_role'] = user.role

        return jsonify(result='ok')
    return jsonify(result='false') # TODO: display feedback

# Documentation

@app.route('/docs/', defaults={'filename': 'index.html'}, strict_slashes=True)
@app.route('/docs/<path:filename>')
def documentation(filename):
    return send_from_directory(app.root_path + '/static/docs/_build/html', filename)


# Documents

@app.route('/list', methods=['GET'])
def list():
    sortables = ['meta_title, meta_provenience, meta_date']
    directions = ['asc', 'desc']
    direction = request.args.get('direction') or 'asc'
    sortby = request.args.get('sort') or 'meta_title'
    if sortby not in sortables:
        sortby = 'meta_title'
    if direction not in directions:
        direction = 'asc'

    documents = Document.query.order_by(sortby + ' ' + direction).all()
    return render_template('pages/documents.html', documents=documents, 
                            direction=direction)

@app.route('/documents', methods=['GET'])
def documents():
    sortables = ['meta_title, meta_provenience, meta_date']
    directions = ['asc', 'desc']
    direction = request.args.get('direction') or 'asc'
    sortby = request.args.get('sort') or 'meta_title'
    if sortby not in sortables:
        sortby = 'meta_title'
    if direction not in directions:
        direction = 'asc'

    user = User.query.filter_by(id=session['user_id']).first()
   
    userdocuments = user.documents.order_by(sortby + ' ' + direction).all()
    return render_template('pages/documents.html', documents=userdocuments, 
                            direction=direction)

# Edit single hand

@app.route('/edit/<int:id>')
def edit(id):
    userlayer = DbHelpers.own('Layertreebank', id)
    if userlayer:
        layerhand = db.session.query(Hand) \
            .filter(userlayer.hand_id==Hand.id).first()
        handdocument = db.session.query(Document) \
            .filter(layerhand.document_id==Document.id).first()
        return render_template('pages/edit.html', ltb=userlayer, 
                                doc=handdocument, hand=layerhand)
    else:
        return redirect(url_for('documents'))

# Ajax calls

@app.route('/import_document', methods=['POST'])
def importdocument():
    url = request.form.get('url').strip()
    result = XmlHelpers.importDocument(url)
    layers = ['original', 'standard', 'variation']
    if result['status'] == 'ok':
        existingdocument = Document.query \
            .filter_by(user_id=session['user_id'], url=url).first()
        if existingdocument is not None:
            data = {'status':'error', 
                    'message': 'You have already imported this document.'}
        else:
            newdocument = Document(url, result['title'], session['user_id'], 
                                   result['xml'], result['html'])
            user = User.query.filter_by(id=session['user_id']).first()
            user.documents.append(newdocument)
            db.session.add(newdocument)
            db.session.commit()
            for i in range(1, result['hands']+1):
                newhand = Hand(newdocument.id, i)
                db.session.add(newhand)
                db.session.commit()
                for k in range(0, 3):
                    newlayer = Layertreebank(layers[k], layers[k], newhand.id)
                    db.session.add(newlayer)
                    db.session.commit()
            data = {'status':'ok'}
    else:
        data = {'status': 'error', 'message': result['message']}

    return jsonify(data)

@app.route('/edit_document', methods=['POST'])
def editdocument():
    id = request.form.get('id').strip()
    meta_date = request.form.get('meta_date').strip()
    meta_provenience = request.form.get('meta_provenience').strip()
    try:
        existingdocument = DbHelpers.own('Document', id)
        if existingdocument is None:
            data = {'status':'error', 
                    'message': 'You don\'t have permission to edit this document.'}
        else:
            existingdocument.meta_date = meta_date
            existingdocument.meta_provenience = meta_provenience
            existingdocument.updated = datetime.today()
            db.session.commit()
            data = {'status':'ok'}
    except Exception:
        return jsonify({'status':'error', 
                        'message': 'Could not change layer name.'})
    return jsonify(data)

@app.route('/delete_document', methods=['POST'])
def deletedocument():
    id = request.form.get('id');
    try:
        existingdocument = DbHelpers.own('Document', id)
        if existingdocument is None:
            data = {'status':'error', 
                    'message': 'You don\'t have permission to delete this document.'}
        else:
            db.session.delete(existingdocument)
            db.session.commit()
            data = {'status':'ok'}
    except Exception:
        return jsonify({'status':'error', 'message': 'Error deleting the document.'})
    return jsonify(data)

@app.route('/edit_hand', methods=['POST'])
def edithand():
    id = request.form.get('id').strip()
    try:
        existinghand = DbHelpers.own('Hand', id)
        if existinghand is None:
            data = {'status':'error', 
                    'message': 'You don\'t have permission to edit this hand.'}
        else:
            existinghand.meta_handwriting_description_edition = request.form \
                .get('meta_handwriting_description_edition').strip()
            existinghand.meta_handwriting_description_custom = request.form \
                .get('meta_handwriting_description_custom').strip()
            existinghand.meta_handwriting_professional = request.form \
                .get('meta_handwriting_professional').strip()
            existinghand.meta_handwriting_same_hand = request.form \
                .get('meta_handwriting_same_hand').strip()
            existinghand.meta_writer_name = request.form \
                .get('meta_writer_name').strip()
            existinghand.meta_writer_title = request.form \
                .get('meta_writer_title').strip()
            existinghand.meta_scribal_name = request.form \
                .get('meta_scribal_name').strip()
            existinghand.meta_scribal_title = request.form \
                .get('meta_scribal_title').strip()
            existinghand.meta_author_name = request.form \
                .get('meta_author_name').strip()
            existinghand.meta_author_title = request.form \
                .get('meta_author_title').strip()
            existinghand.meta_text_type = request.form \
                .get('meta_text_type').strip()
            existinghand.meta_addressee = request.form \
                .get('meta_addressee').strip()
            existinghand.meta_addressee_name = request.form \
                .get('meta_addressee_name').strip()
            existinghand.meta_addressee_title = request.form \
                .get('meta_addressee_title').strip()
            existinghand.updated = datetime.today()
            db.session.commit()
            data = {'status':'ok'}
    except Exception:
        print str(traceback.format_exc())
        return jsonify({'status':'error', 
                        'message': 'Could not change layer name.'})
    return jsonify(data)

@app.route('/delete_layertreebank', methods=['POST'])
def deletelayertreebank():
    id = request.form.get('id');
    try:
        existinglayertreebank = DbHelpers.own('Layertreebank', id)
        if existinglayertreebank is None:
            data = {'status':'error', 
                    'message': 'You don\'t have permission to delete this document.'}
        else:
            existinglayertreebank.body = ''
            db.session.commit()
            data = {'status':'ok'}
    except Exception:
        return jsonify({'status':'error', 
                        'message': 'Error deleting the document.'})
    return jsonify(data)

@app.route('/get_treebank_xml', methods=['POST'])
def gettreebankxml():
    id = request.form.get('id');
    print id
    try:
        existinglayertreebank = DbHelpers.own('Layertreebank', id)
        if existinglayertreebank is None:
            data = {'status':'error', 'message': 'No permission.'}
        else:
            data = {'status':'ok', 'xml':existinglayertreebank.body}
    except Exception:
        return jsonify({'status':'error', 
                        'message': 'Could not retrieve the treebank.'})
    return jsonify(data)

@app.route('/save_paths', methods=['POST'])
def savepaths():

    settings = request.form.get('paths').strip()
    id = request.form.get('id');

    try:
        existinglayertreebank = DbHelpers.own('Layertreebank', id)
        if existinglayertreebank is None:
            data = {'status':'error', 'message': 'No permission.'}
        else:
            existinglayertreebank.settings = settings
            db.session.commit()
            data = {'status':'ok'}
    except Exception:
        return jsonify({'status':'error', 
                        'message': 'Could not retrieve the treebank.'})
    return jsonify(data)

# File uploads

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload_layertreebank', methods=['POST'])
def uploadlayertreebank():
    
    try:
        file = request.files['file']
        id = request.form.get('id')
        if allowed_file(file.filename):
            
            existinghand = DbHelpers.own('Layertreebank', id)

            if existinghand is not None:
                existinghand.body = file.read()
                db.session.commit()
                flash('Treebank added')
            else:
                flash('Operation not allowed')
        else:
            filetypes = ", ".join(str(x) for x in app.config['ALLOWED_EXTENSIONS'])
            flash('Allowed file types: '+filetypes+'.')

    except Exception:
        print(traceback.format_exc())
        flash('An error occurred')
    return redirect('/edit/'+id)

# File uploads: ajax

@app.route('/add_layertreebank', methods=['GET', 'POST'])
def addlayertreebank():
    try:
        file = request.files['file']
        id = request.form.get('id')
        print id
        if allowed_file(file.filename):
            
            existinghand = DbHelpers.own('Layertreebank', id)

            if existinghand is not None:
                existinghand.body = file.read()
                db.session.commit()
                data = {'status':'ok'}
            else:
                data = {'status':'error', 'message': 'Operation not allowed'}
        else:
            filetypes = ", ".join(str(x) for x in app.config['ALLOWED_EXTENSIONS'])
            data = {'status':'error', 
                    'message': 'Allowed file types: '+filetypes+'.'}
            
    except Exception:
        print(traceback.format_exc())
        data = {'status':'error', 'message': 'An error occurred.'}
    return jsonify(data)


