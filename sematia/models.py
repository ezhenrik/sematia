from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import mapper

db = SQLAlchemy()

class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_count = db.Column(db.Integer)
    standard_count = db.Column(db.Integer)
    variation_count = db.Column(db.Integer)

    def __init__(self, original_count, standard_count, variation_count):
        self.original_count = original_count
        self.standard_count = standard_count
        self.variation_count = variation_count

userdocument = db.Table('userdocument',
                   db.Column('id', db.Integer, primary_key=True),
                   db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                   db.Column('document_id', db.Integer, db.ForeignKey('document.id'))
               )

class Userdocument(object):
    __tablename__ = 'userdocument'
    query = db.session.query_property()
    def __init__(self, user_id, document_id):
        self.user_id = user_id
        self.document_id = document_id

mapper(Userdocument, userdocument)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    auth_id = db.Column(db.String(120), unique=True)
    auth_provider = db.Column(db.String(80))
    created = db.Column(db.DateTime, default=datetime.today())
    role = db.Column(db.Integer)

    def __init__(self, name, role, auth_id, auth_provider):
        self.name = name
        self.role = role
        self.auth_id = auth_id
        self.auth_provider = auth_provider

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256))
    meta_title = db.Column(db.String(256))
    meta_date = db.Column(db.String(256))
    meta_date_not_before = db.Column(db.String(256))
    meta_date_not_after = db.Column(db.String(256))
    meta_provenience = db.Column(db.String(256))
    xml = db.Column(db.UnicodeText(4294967295))
    html = db.Column(db.UnicodeText(4294967295))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, default=datetime.today())
    updated = db.Column(db.DateTime)
    hands = db.relationship('Hand', backref='document', 
                             cascade="all, delete-orphan",
                             lazy='dynamic')
    users = db.relationship('User', secondary=userdocument,
        backref=db.backref('documents', lazy='dynamic'))

    messages = db.relationship('Message', backref='document',
                                cascade="all, delete-orphan")

    def __init__(self, url, xml, html, title, date_not_before, 
            date_not_after, provenience):
        self.url = url
        self.xml = xml
        self.html = html
        self.meta_title = title
        self.meta_date_not_before = date_not_before,
        self.meta_date_not_after = date_not_after,
        self.meta_provenience = provenience

class Hand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    hand_no = db.Column(db.Integer)
    hand_id = db.Column(db.String(256))
    hand_name = db.Column(db.String(256))
    created = db.Column(db.DateTime, default=datetime.today())
    updated = db.Column(db.DateTime)
    meta_handwriting_description_edition = db.Column(db.UnicodeText())
    meta_handwriting_description_custom = db.Column(db.UnicodeText())
    meta_handwriting_professional = db.Column(db.UnicodeText())
    meta_handwriting_same_hand = db.Column(db.UnicodeText())

    meta_writer_name = db.Column(db.UnicodeText())
    meta_writer_title = db.Column(db.UnicodeText())
    meta_writer_trismegistos_id = db.Column(db.UnicodeText())

    meta_scribal_name = db.Column(db.UnicodeText())
    meta_scribal_title = db.Column(db.UnicodeText())
    meta_scribal_trismegistos_id = db.Column(db.UnicodeText())

    meta_author_name = db.Column(db.UnicodeText())
    meta_author_title = db.Column(db.UnicodeText())
    meta_author_trismegistos_id = db.Column(db.UnicodeText())

    meta_text_type = db.Column(db.UnicodeText())

    meta_addressee = db.Column(db.UnicodeText())
    meta_addressee_name = db.Column(db.UnicodeText())
    meta_addressee_title = db.Column(db.UnicodeText())
    meta_addressee_trismegistos_id = db.Column(db.UnicodeText())
    layertreebanks = db.relationship('Layertreebank', backref='hand', 
                                      cascade="all, delete-orphan", 
                                      lazy='dynamic')

    def __init__(self, document_id, hand_no, hand_name):
        self.document_id = document_id
        self.hand_no = hand_no
        self.hand_name = hand_name

class Layertreebank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    type = db.Column(db.String(80))
    hand_id = db.Column(db.Integer, db.ForeignKey('hand.id'))
    body = db.Column(db.UnicodeText(4294967295))
    settings = db.Column(db.UnicodeText(4294967295))
    plaintext = db.Column(db.UnicodeText(4294967295))
    created = db.Column(db.DateTime, default=datetime.today())
    updated = db.Column(db.DateTime)
    approved_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    arethusa_id = db.Column(db.Integer)
    arethusa_publication_id = db.Column(db.Integer)

    def __init__(self, name, type, hand_id):
        self.name = name
        self.type = type
        self.hand_id = hand_id

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.UnicodeText(4294967295))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'))
    created = db.Column(db.DateTime, default=datetime.today())
    updated = db.Column(db.DateTime)
    user = db.relationship('User', backref='message')


    def __init__(self, body, user_id, document_id):
        self.body = body
        self.user_id = user_id
        self.document_id = document_id
