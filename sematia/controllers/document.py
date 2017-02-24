from datetime import datetime
import urllib.request

from flask import session

from .. import models
from ..utils import log, xml

Log = log.Log
Xml = xml.Xml
db = models.db

class Document():

    @staticmethod
    def get(id):
        return models.Document.query.get(id)

    @staticmethod
    def get_all():
        return models.Document.query.all()

    @staticmethod
    def get_editable(id):
        if models.Userdocument.query.filter_by(
                document_id=id, user_id=session['user_id']).first() or \
                session['user_admin']:
            return models.Document.query.get(id)

    @staticmethod
    def add(url):
        try:
            if models.Document.query.filter_by(url=url).first():
                data = {'status':'error', 
                        'message': 'This document already exists in Sematia.'}
            else:
                with urllib.request.urlopen(url) as doc_url:
                    s = doc_url.read().decode('utf-8')
                data = Xml.start(s)
                
                document = models.Document(
                    url, 
                    data['html'],
                    data['title'], 
                    data['date_not_before'],
                    data['date_not_after'],
                    data['provenience'])
                db.session.add(document)
                db.session.commit()

                userdocument = models.Userdocument(user_id=session['user_id'], 
                                            document_id=document.id)
                db.session.add(userdocument)

                db.session.commit()

                layers = ['original', 'standard', 'variation']

                for i in range(0, len(data['hands'])):
                    hand = models.Hand(document.id, i+1, data['hands'][i])
                    db.session.add(hand)
                    db.session.commit()
                    for k in range(0, 3):
                        layer = models.Layertreebank(layers[k], layers[k], 
                                                     hand.id)
                        db.session.add(layer)
                        db.session.commit()
                data = {'status':'ok'}

        except Exception:
            Log.e()
            return {'status':'error', 'message': 'Please check the URL'}
        return data

    @staticmethod
    def edit(id, meta_title, meta_date_not_before, meta_date_not_after, 
             meta_provenience):
        data = {'status':'init'}
        try:
            document = Document.get_editable(id)
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
            return {'status':'error', 'message': 'Could not edit the document.'}
        return data

    @staticmethod
    def delete(id):
        try:
            document = Document.get_editable(id)
            if document:
                db.session.delete(document)
                db.session.commit()
                data = {'status':'ok'}
            else:
                data = {'status':'error'}

        except Exception:
            Log.e()
            return {'status':'error', 'message': 'Error deleting the document.'}
        return data
