from datetime import datetime

from flask import session

from .. import models
from ..utils import log

Log = log.Log
db = models.db

class User():

    @staticmethod
    def get_contributors(ids):
        contributors = []
        all_users = []
        
        users = models.User.query.filter(models.User.id.in_(ids)).all()
        for user in users:
            contributor = {
                'name': user.name,
                'id': user.id,
                'you': int(user.id == session['user_id'])
            }
            contributors.append(contributor)

        users = models.User.query.all()
        for user in users:
            u = {
                'label': user.name,
                'value': user.id,
            }
            all_users.append(u)

        return {'contributors': contributors, 'all_users':all_users}