from datetime import datetime

from flask import session

from . import document
from .. import models
from ..utils import log

db = models.db
Document = document.Document
Log = log.Log

class Hand():

    @staticmethod
    def get_all(document_id):
        document = models.Document.query.filter_by(id=document_id).first()
        return document.hands.all()

    @staticmethod
    def get_editable(id):
        doc_id = models.Hand.query.get(id).document_id
        if Document.get_editable(doc_id):
            return models.Hand.query.get(id)

    @staticmethod
    def edit(
        id,
        meta_handwriting_description_edition,
        meta_handwriting_description_custom,
        meta_handwriting_professional,
        meta_handwriting_same_hand,
        meta_writer_name,
        meta_writer_title,
        meta_writer_trismegistos_id,
        meta_scribal_name,
        meta_scribal_title,
        meta_scribal_trismegistos_id,
        meta_author_name,
        meta_author_title,
        meta_author_trismegistos_id,
        meta_text_type,
        meta_addressee,
        meta_addressee_name,
        meta_addressee_title,
        meta_addressee_trismegistos_id
    ):
        try:
            hand = Hand.get_editable(id)
            if hand:
                hand.meta_handwriting_description_edition = meta_handwriting_description_edition
                hand.meta_handwriting_description_custom = meta_handwriting_description_custom
                hand.meta_handwriting_professional = meta_handwriting_professional
                hand.meta_handwriting_same_hand = meta_handwriting_same_hand
                hand.meta_writer_name = meta_writer_name
                hand.meta_writer_title = meta_writer_title
                hand.meta_writer_trismegistos_id = meta_writer_trismegistos_id or 0
                hand.meta_scribal_name = meta_scribal_name
                hand.meta_scribal_title = meta_scribal_title
                hand.meta_scribal_trismegistos_id = meta_scribal_trismegistos_id or 0
                hand.meta_author_name = meta_author_name
                hand.meta_author_title = meta_author_title
                hand.meta_author_trismegistos_id = meta_author_trismegistos_id or 0
                hand.meta_text_type = meta_text_type
                hand.meta_addressee = meta_addressee
                hand.meta_addressee_name = meta_addressee_name
                hand.meta_addressee_title = meta_addressee_title
                hand.meta_addressee_trismegistos_id = meta_addressee_trismegistos_id or 0
                hand.updated = datetime.today()
                db.session.commit()
                data = {'status':'ok'}

        except Exception:
            Log.e()
            return {'status':'error', 'message': 'Could not edit the hand.'}
        return data

    