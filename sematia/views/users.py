from datetime import datetime
import traceback

from flask import Blueprint, render_template, session, jsonify, redirect, \
                  url_for, request

from ..controllers import document, hand, layertreebank, user, \
                          userdocument

users = Blueprint('users', __name__)

Document = document.Document
Hand = hand.Hand
Layertreebank = layertreebank.Layertreebank
User = user.User
Userdocument = userdocument.Userdocument

@users.route('/')
def index():
    users = Records.all('User')
    return render_template('pages/users.html', users=users, user_id=session['user_id'])