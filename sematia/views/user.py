import json
import requests
from .. import app

from flask import Blueprint, jsonify, redirect, render_template, \
                  request, session, url_for

from oauth2client import client, crypt

from ..models import db, User
from ..utils import log

user = Blueprint('user', __name__)
Log = log.Log


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
    session.pop('user_role', None)
    session.pop('user_admin', None)
    session.pop('perseids', None)
    return redirect(url_for('user.index'))

@user.route('/oauth')
def oauth():
    code = request.args.get('code')

    if code:
        Log.p('code: '+code)
        url = 'https://sosol.perseids.org/sosol/oauth/token'
        payload = {
            'code': code,
            'client_id': app.app.config['PERSEIDS_CLIENT_ID'],
            'client_secret': app.app.config['PERSEIDS_CLIENT_SECRET'],
            'grant_type': 'authorization_code',
            'redirect_uri': app.app.config['PERSEIDS_REDIRECT_URI']
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        Log.p(payload)
        r = requests.post(url, data=payload, headers=headers)
        r_json = r.json()
        if 'access_token' in r_json:
            Log.p(r_json['access_token'])
            Log.p('success!')
            session['perseids'] = r_json['access_token']
            return render_template('pages/perseids-success.html')
        else:
            Log.p('error!')
            return 'An error occurred.'


@user.route('/perseids_validate',  methods=['POST'])
def perseids_validate():
    if ('perseids' in session):
        access_token = session['perseids']

        url = 'https://sosol.perseids.org/sosol/api/v1/user'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer '+access_token
        }
        r = requests.get(url, headers=headers)
        Log.p(r.status_code)
        if r.status_code == 200:
            r_json = r.json()
            Log.p(r_json)

            if 'user' in r_json:
                return 'ok'
    return 'noaccess'


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
        if not user.role:
            user.role = 0
    else:
        user = User(idinfo['name'], 1, userid, 'google')
        db.session.add(user)
    db.session.commit()

    session['user_name'] = user.name
    session['user_id'] = user.id
    session['user_role'] = user.role
    session['user_admin'] = user.role > 1
    return url_for('documents.index')
