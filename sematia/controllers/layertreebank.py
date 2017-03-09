import zipfile
import io
import time

from flask import session, send_file

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
    def get_all():
        return models.Layertreebank.query.all()

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

    @staticmethod
    def update_arethusa(id, arethusa_id, arethusa_publication_id):
        try:
            layertreebank = Layertreebank.get_editable(id)
            if layertreebank:
                layertreebank.arethusa_id = arethusa_id
                layertreebank.arethusa_publication_id = arethusa_publication_id
                db.session.commit()
                data = {'status':'ok'}
        except Exception:
            return {'status':'error', 
                            'message': 'Could not retrieve the treebank.'}
        return data

    @staticmethod
    def store_plaintext(id, text):
        try:
            layertreebank = Layertreebank.get_editable(id)
            if layertreebank:
                layertreebank.plaintext = text
                db.session.commit()
                data = {'status':'ok'}
        except Exception:
            return {'status':'error', 
                            'message': 'Could not retrieve the treebank.'}
        return data

    @staticmethod
    def validate_word_counts():
        data = {
            'status': 'error',
            'message': 'Failed to test for word counts'
        }
        hand_counts = {}
        erroneous = {}
        layertreebanks = Layertreebank.get_all()
        if layertreebanks:
            for lt in layertreebanks:
                if lt.body:
                    if lt.hand_id not in hand_counts:
                        hand_counts[lt.hand_id] = []
                    hand_counts[lt.hand_id].append(Xml.count_words(lt.body))

        for hc in hand_counts:
            if not len(set(hand_counts[hc])) <= 1:
                hand = models.Hand.query.get(hc)
                hand_no = hand.hand_no
                hand_document = models.Document.query.get(hand.document_id).meta_title
                erroneous[str(hand_document)+', hand '+str(hand_no)] = hand_counts[hc]

        if erroneous:
            msg = ''
            for er in erroneous:
                msg += er+': '+str(erroneous[er])+'\n'

            data['message'] = msg

        else:
            data = {
                'status':'ok', 
            }
        return data

    @staticmethod
    def export(target):
        treebanks = Layertreebank.get_all()
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:

            for treebank in treebanks:
                if treebank.body:
                    if target is 'all' or target == treebank.type:
                        data = zipfile.ZipInfo(str(treebank.id)+'.xml')
                        data.date_time = time.localtime(time.time())[:6]
                        data.compress_type = zipfile.ZIP_DEFLATED
                        zf.writestr(data, str.encode(treebank.body))
        memory_file.seek(0)
        return memory_file

        
