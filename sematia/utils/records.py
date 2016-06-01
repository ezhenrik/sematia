import traceback

from flask import session

from ..models import db, User, Document, Hand, Layertreebank

class Records():

    model_map = {
        'User':User,
        'Document':Document,
        'Hand':Hand,
        'Layertreebank':Layertreebank
    }

    @classmethod
    def get(cls, model, id):
        model = cls.model_map[model]
        if isinstance(id, str) or isinstance(id, int):
            return model.query.get(id)
        else:
            return model.query.filter(model.id.in_(id)).all()

    @classmethod
    def all(cls, model):
        model = cls.model_map[model]
        return model.query.all()