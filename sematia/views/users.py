from datetime import datetime
import traceback

from flask import Blueprint, render_template, session, jsonify, redirect, \
                  url_for, request

from ..controllers import documents
from ..utils import records

users = Blueprint('users', __name__)
Records = records.Records

@users.route('/')
def index():
    users = Records.all('User')
    return render_template('pages/users.html', users=users, user_id=session['user_id'])