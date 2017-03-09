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
                        hand = treebank.hand
                        document = hand.document
                        metadata = """\
   <sematia>
      <id>%s</id>
      <document_title>%s</document_title>
      <document_provenience>%s</document_provenience>
      <document_date_not_before>%s</document_date_not_before>
      <document_date_not_after>%s</document_date_not_after>

      <hand_no>%s</hand_no>
      <hand_name>%s</hand_name>

      <meta_handwriting_description_edition>%s</meta_handwriting_description_edition>
      <meta_handwriting_description_custom>%s</meta_handwriting_description_custom>
      <meta_handwriting_professional>%s</meta_handwriting_professional>
      <meta_handwriting_same_hand>%s</meta_handwriting_same_hand>

      <meta_writer_name>%s</meta_writer_name>
      <meta_writer_title>%s</meta_writer_title>
      <meta_writer_trismegistos_id>%s</meta_writer_trismegistos_id>

      <meta_scribal_name>%s</meta_scribal_name>
      <meta_scribal_title>%s</meta_scribal_title>
      <meta_scribal_trismegistos_id>%s</meta_scribal_trismegistos_id>

      <meta_author_name>%s</meta_author_name>
      <meta_author_title>%s</meta_author_title>
      <meta_author_trismegistos_id>%s</meta_author_trismegistos_id>

      <meta_text_type>%s</meta_text_type>

      <meta_addressee>%s</meta_addressee>
      <meta_addressee_name>%s</meta_addressee_name>
      <meta_addressee_title>%s</meta_addressee_title>
      <meta_addressee_trismegistos_id>%s</meta_addressee_trismegistos_id>
   </sematia>\n
                        """ % (treebank.id, 
                               document.meta_title,
                               document.meta_provenience,
                               document.meta_date_not_before,
                               document.meta_date_not_after,
                               hand.hand_no, 
                               hand.hand_name,
                               hand.meta_handwriting_description_edition,
                               hand.meta_handwriting_description_custom,
                               hand.meta_handwriting_professional,
                                hand.meta_handwriting_same_hand,

                                hand.meta_writer_name,
                                hand.meta_writer_title,
                                hand.meta_writer_trismegistos_id or '',

                                hand.meta_scribal_name,
                                hand.meta_scribal_title,
                                hand.meta_scribal_trismegistos_id or '',

                                hand.meta_author_name,
                                hand.meta_author_title,
                                hand.meta_author_trismegistos_id or '',

                                hand.meta_text_type,

                                hand.meta_addressee,
                                hand.meta_addressee_name,
                                hand.meta_addressee_title,
                                hand.meta_addressee_trismegistos_id or ''
                               )

                        xml_data = Xml.add_metadata(treebank.body, metadata)
                        
                        zf.writestr(data, xml_data)
        memory_file.seek(0)

        return memory_file

        
