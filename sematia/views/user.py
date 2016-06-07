import json
import requests
from .. import app

from flask import Blueprint, jsonify, redirect, render_template, \
                  request, session, url_for

from oauth2client import client, crypt

from ..models import db, User

user = Blueprint('user', __name__)


@user.route('/')
def index():
    if 'user_id' not in session:
        return render_template('pages/signin.html')
    else:
        return redirect(url_for('documents.index'))

@user.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('user.index'))

@user.route('/tokensignin',  methods=['POST'])
def tokensignin():
    token = request.form['idtoken']
    try:
        idinfo = client.verify_id_token(token, app.app.config['GOOGLE_CLIENT_ID'])
    except crypt.AppIdentityError:
        return redirect(url_for('/logout'))
    userid = idinfo['sub']

    user = User.query.filter_by(auth_id=userid).first()
    if user:
        user.name = idinfo['name']
    else:
        user = User(idinfo['name'], 1, userid, 'google')
        db.session.add(user)
    db.session.commit()

    session['user_name'] = idinfo['name']
    session['user_id'] = user.id
    session['user_role'] = user.role
    session['user_admin'] = user.role > 1
    return url_for('documents.index')
