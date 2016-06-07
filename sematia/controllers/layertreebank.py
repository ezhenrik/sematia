from flask import session

from . import document
from .. import models
from ..utils import log, xml

db = models.db
Document = document.Document
Log = log.Log
Xml = xml.Xml

class Layertreebank():

    @staticmethod
    def get(id):
        return models.Layertreebank.query.get(id)

    @staticmethod
    def get_editable(id):
        doc_id = models.Layertreebank.query.get(id).hand.document_id
        if Document.get_editable(doc_id):
            return models.Layertreebank.query.get(id)

    @staticmethod
    def get_treebank(id):
        layertreebank = models.Layertreebank.query.filter_by(id=id).first()
        if layertreebank:
            return {'status':'ok', 'data':layertreebank.body, 
                'approve':layertreebank.approved_user_id}
        else:
            return {'status':'error'}

    @staticmethod
    def add_treebank(id, file):
        try:
            layertreebank = Layertreebank.get_editable(id)
            if layertreebank:
                if '.' in file.filename and \
                        file.filename.rsplit('.', 1)[1] in ['xml', 'txt']:
                    contents = file.read().decode('utf-8')
                    if Xml.validate(contents):
                        layertreebank.body = contents
                        db.session.commit()
                        data = {'status':'ok', 'mode': 'added'}
                    else:
                        data = {'status':'error', 'message': 'Please validate the XML.'}
        except Exception:
            Log.e()
            return data
        return data

    @staticmethod
    def delete_treebank(id):
        layertreebank = Layertreebank.get_editable(id)
        if layertreebank:
            layertreebank.body = ''
            layertreebank.approved_user_id = None
            db.session.commit()
            return {'status':'ok', 'mode': 'deleted'}
        else:
            return {'status':'error'}

    @staticmethod
    def update_treebank(id, status):
        if 'user_admin' in session and session['user_admin']:
            layertreebank = models.Layertreebank.query.get(id)
            if layertreebank:
                if status == '0':
                    layertreebank.approved_user_id = session['user_id']
                else:
                    layertreebank.approved_user_id = None
                db.session.commit()
                return {'status':'ok'}
            else:
                return {'status':'error'}

    @staticmethod
    def update_settings(id, settings):
        try:
            layertreebank = Layertreebank.get_editable(id)
            if layertreebank:
                layertreebank.settings = settings
                db.session.commit()
                data = {'status':'ok'}
        except Exception:
            return {'status':'error', 
                            'message': 'Could not retrieve the treebank.'}
        return data
