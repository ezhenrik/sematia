# -*- coding: utf-8 -*-

import os
import difflib
import re
import xml.etree.ElementTree as etree
import fnmatch
import traceback
import urllib.request

from datetime import datetime

from flask import session, jsonify

from ..models import db, User, Document, Hand, Layertreebank, Userdocument
from ..utils import log, records, xml

Records = records.Records
Log = log.Log


class Documents():

    @staticmethod
    def get_hands(document_id):
        document = Document.query.filter_by(id=document_id).first()
        return document.hands.all()

    @staticmethod
    def get_treebank(id):
        layertreebank = Layertreebank.query.filter_by(id=id).first()
        if layertreebank:
            return jsonify({'status':'ok', 'data':layertreebank.body, 
                'approve':layertreebank.approved_user_id})
        else:
            return jsonify({'status':'error'})

    @staticmethod
    def delete_treebank(id):
        layertreebank = Layertreebank.query.filter_by(id=id).first()
        if layertreebank:
            my_document = Userdocument.query.filter_by(
                document_id=layertreebank.hand.document.id, 
                    user_id=session['user_id']).first()
            if my_document:
                layertreebank.body = ''
                layertreebank.approved_user_id = None
                db.session.commit()
                return jsonify({'status':'ok', 'mode': 'deleted'})
        else:
            return jsonify({'status':'error'})

    @staticmethod
    def update_treebank(id, status):
        layertreebank = Layertreebank.query.filter_by(id=id).first()
        if layertreebank:
            if status == '0':
                layertreebank.approved_user_id = session['user_id']
            else:
                layertreebank.approved_user_id = None
            db.session.commit()
            return jsonify({'status':'ok'})
        else:
            return jsonify({'status':'error'})

    @staticmethod
    def add_document(url):
        try:

            if Document.query.filter_by(url=url).first():
                data = {'status':'error', 
                        'message': 'This document already exists in Sematia.'}
            else:
                with urllib.request.urlopen(url) as doc_url:
                    s = doc_url.read().decode('utf-8')
                data = xml.Xml.start(s)

                print(data)

                document = Document(
                    url, 
                    data['html'],
                    data['title'], 
                    data['date_not_before'],
                    data['date_not_after'],
                    data['provenience']
                )
                db.session.add(document)
                db.session.commit()

                userdocument = Userdocument(user_id=session['user_id'], 
                                            document_id=document.id)
                db.session.add(userdocument)

                db.session.commit()

                layers = ['original', 'standard', 'variation']

                for i in range(1, data['hands']+1):
                    hand = Hand(document.id, i)
                    db.session.add(hand)
                    db.session.commit()
                    for k in range(0, 3):
                        layer = Layertreebank(layers[k], layers[k], hand.id)
                        db.session.add(layer)
                        db.session.commit()
                data = {'status':'ok'}

        except Exception:
            Log.e()
            return jsonify({'status':'error', 'message': 'Please check the URL'})
        return jsonify(data)

    @staticmethod
    def delete_document(id):
        try:
            if Userdocument.query.filter_by(document_id=id, 
                    user_id=session['user_id']).first():
                db.session.delete(Document.query.get(id))
                db.session.commit()
                data = {'status':'ok'}
            else:
                data = {'status':'error'}

        except Exception:
            Log.e()
            return jsonify({'status':'error', 'message': 'Error deleting the document.'})
        return jsonify(data)

    @staticmethod
    def remove_contributor(id, document_id):
        try:
            userdocument = Userdocument.query.filter_by(document_id=document_id, 
                    user_id=id).first()
            if userdocument:
                db.session.delete(userdocument)
                db.session.commit()
                data = {'status':'ok'}
            else:
                data = {'status':'error'}

        except Exception:
            Log.e()
            return jsonify({'status':'error', 'message': 'Error removing the contributor.'})
        return jsonify(data)

    @staticmethod
    def add_contributor(id, document_id):
        try:
            userdocument = Userdocument.query.filter_by(document_id=document_id, 
                    user_id=id).first()
            if not userdocument:
                userdocument = Userdocument(user_id=id, document_id=document_id)
                db.session.add(userdocument)
                db.session.commit()
                data = {'status':'ok'}
            else:
                data = {'status':'error'}

        except Exception:
            Log.e()
            return jsonify({'status':'error', 'message': 'Error adding the contributor.'})
        return jsonify(data)

    @staticmethod
    def edit_document(id, meta_title, meta_date_not_before, meta_date_not_after, 
            meta_provenience):
        data = {'status':'init'}
        try:
            userdocument = Userdocument.query.filter_by(document_id=document_id, 
                    user_id=session['user_id']).first()
            if userdocument:
                document = Document.query.filter_by(id=id).first()
                if document:
                    document.meta_title = meta_title
                    document.meta_date_not_before = meta_date_not_before
                    document.meta_date_not_after = meta_date_not_after
                    document.meta_provenience = meta_provenience
                    document.updated = datetime.today()
                    db.session.commit()
                    data = {'status':'ok'}

        except Exception:
            Log.e()
            return jsonify({'status':'error', 
                            'message': 'Could not edit the document.'})
        return jsonify(data)

    @staticmethod
    def edit_hand(
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
    ):
        data = {'status':'init'}
        try:
            hand = Hand.query.filter_by(id=id).first()
            if hand:
                document_id = hand.document.id
                userdocument = Userdocument.query.filter_by(document_id=document_id, 
                    user_id=session['user_id']).first()
                if userdocument:
                    hand.meta_handwriting_description_edition = meta_handwriting_description_edition
                    hand.meta_handwriting_description_custom = meta_handwriting_description_custom
                    hand.meta_handwriting_professional = meta_handwriting_professional
                    hand.meta_handwriting_same_hand = meta_handwriting_same_hand
                    hand.meta_writer_name = meta_writer_name
                    hand.meta_writer_title = meta_writer_title
                    hand.meta_scribal_name = meta_scribal_name
                    hand.meta_scribal_title = meta_scribal_title
                    hand.meta_author_name = meta_author_name
                    hand.meta_author_title = meta_author_title
                    hand.meta_text_type = meta_text_type
                    hand.meta_addressee = meta_addressee
                    hand.meta_addressee_name = meta_addressee_name
                    hand.meta_addressee_title = meta_addressee_title
                    hand.updated = datetime.today()
                    db.session.commit()
                    data = {'status':'ok'}

        except Exception:
            log.e()
            return jsonify({'status':'error', 
                            'message': 'Could not edit the document.'})
        return jsonify(data)

    