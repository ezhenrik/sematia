from datetime import datetime

from flask import session

from . import document
from . import userdocument
from .. import models
from ..utils import log

db = models.db
Document = document.Document
Userdocument = userdocument.Userdocument
Log = log.Log

class Message():

    f = '%-d %B %Y, %H:%M'

    @staticmethod
    def get_editable(id):
        return models.Message.query.filter_by(
                id=id, user_id=session['user_id']).first() or \
                session['user_admin']

    @classmethod
    def get_my(cls):
        try:
            data = {}
            messages = models.Message.query.join(
                models.Userdocument, models.Userdocument.user_id==session['user_id'] 
                    and models.Userdocument.document_id==models.Message.document_id) \
                .filter(
                        models.Userdocument.user_id==session['user_id'], 
                        models.Userdocument.document_id==models.Message.document_id
                        ) \
                .join(models.User, models.User.id==models.Message.user_id) \
                .join(models.Document, models.Document.id==models.Message.document_id) \
                .add_columns(models.User.name) \
                .add_columns(models.Document.meta_title) \
                .order_by(
                    models.Message.created.desc()
                ).all()

            if messages:
                    message_dict = [{'created':a, 'body':b, 'user':c, 'title':d, 'id':e, 'owner':f} 
                                       for a,b,c,d,e, f in zip(
                                        [m[0].created.strftime(cls.f) for m in messages],
                                        [m[0].body for m in messages], 
                                        [m.name for m in messages], 
                                        [m.meta_title for m in messages], 
                                        [m[0].id for m in messages], 
                                        [m[0].user_id == session['user_id'] for m in messages]
                                        )]
                    data = message_dict
        except:
            Log.e()
        return data


    @classmethod
    def get_document_messages(cls, doc_id):
        data = {}
        try:
            messages = models.Message.query.filter_by(document_id=doc_id).join(models.User, models.User.id==models.Message.user_id).add_columns(models.User.name).order_by(models.Message.created.asc()).all()
            message_dict = {}
            if messages:
                message_dict = [{'created':a, 'body':b, 'user':c, 'id':d, 'owner':e} 
                                   for a,b,c,d,e in zip(
                                    [m[0].created.strftime(cls.f) for m in messages],
                                    [m[0].body for m in messages], 
                                    [m[1] for m in messages], 
                                    [m[0].id for m in messages], 
                                    [m[0].user_id == session['user_id'] for m in messages]
                                    )]
                data = {'messages': message_dict}
        except:
            Log.e()
        return data

    @classmethod
    def add(cls, doc_id, body):
        data = {}
        try:
            if Document.get_editable(doc_id) and body.strip() != '':
                message = models.Message(body, session['user_id'], doc_id)
                db.session.add(message)
                db.session.commit()
                data = {'status':'ok', 'body': message.body, 'id':message.id, 'created':message.created.strftime(cls.f)}
        except:
            Log.e()
        return data

    @staticmethod
    def delete(id):
        data = {}
        print(session['user_id'])
        try:
            if Message.get_editable(id):
                message = models.Message.query.get(id)
                db.session.delete(message)
                db.session.commit()
                data = {'status':'ok'}
        except:
            Log.e()
        return data