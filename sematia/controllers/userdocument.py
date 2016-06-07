from datetime import datetime

from flask import session

from . import document
from .. import models
from ..utils import log

db = models.db
Document = document.Document
Log = log.Log


class Userdocument():

    @staticmethod
    def get_editable(id, user_id):
        return models.Userdocument.query.filter_by(document_id=document_id, 
                    user_id=user_id).first() or session['user_admin']

    @staticmethod
    def add(user_id, document_id):
        try:
            if Document.get_editable(document_id):
                userdocument = models.Userdocument.query.filter_by(
                    document_id=document_id, user_id=user_id).first()
                if not userdocument:
                    userdocument = models.Userdocument(user_id=user_id, 
                                                       document_id=document_id)
                    db.session.add(userdocument)
                    db.session.commit()
                    data = {'status':'ok', 
                            'owner': int(user_id)==int(session['user_id'])}
                else:
                    data = {'status':'error'}

        except Exception:
            Log.e()
            return {'status':'error', 'message': 'Error adding the contributor.'}
        return data

    @staticmethod
    def delete(user_id, document_id):
        try:
            userdocument = Userdocument.get_editable(document_id, user_id)
            userdocument_count = models.Userdocument \
                .query.filter_by(document_id=document_id).count()
            if userdocument and userdocument_count > 1:
                db.session.delete(userdocument)
                db.session.commit()
                data = {'status':'ok'}
            else:
                data = {'status':'error'}

        except Exception:
            Log.e()
            return {'status':'error', 'message': 'Error removing the contributor.'}
        return data