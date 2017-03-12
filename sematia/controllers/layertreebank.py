import zipfile
import io
import time
import xml.etree.ElementTree as etree
import re
import unicodedata
from flask import session, send_file

from sqlalchemy import or_

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
    def get_filtered(filters):
        return models.Hand.query.join(models.Document).filter(*filters).all()

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
      <type>%s</type>
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
                               treebank.type,
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

    @staticmethod
    def export_words(target):

        treebanks = Layertreebank.get_all()
        memory_file = io.BytesIO()

        with zipfile.ZipFile(memory_file, 'w') as zf:

            for treebank in treebanks:
                if treebank.body:
                    if target is 'all' or target == treebank.type:
                        data = zipfile.ZipInfo(str(treebank.id)+'.csv')
                        data.date_time = time.localtime(time.time())[:6]
                        data.compress_type = zipfile.ZIP_DEFLATED
                        word_data = Xml.get_word_data(treebank.body)
                        
                        zf.writestr(data, word_data)
        memory_file.seek(0)

        return memory_file

    @staticmethod
    def search(query, options):
        hand_args = []
        if options['document_title']:
            if options['document_title_mode'] == 'exact':
                hand_args.append(models.Document.meta_title == options['document_title'])
            elif options['document_title_mode'] == 'begins':
                hand_args.append(models.Document.meta_title.like(options['document_title']+'%'))
            elif options['document_title_mode'] == 'contains':
                hand_args.append(models.Document.meta_title.like('%'+options['document_title']+'%'))
            elif options['document_title_mode'] == 'ends':
                hand_args.append(models.Document.meta_title.like('%'+options['document_title']))
            elif options['document_title_mode'] == 'regex':
                hand_args.append(models.Document.meta_title.op('regexp')(options['document_title']))
        if options['document_provenience']:
            if options['document_provenience_mode'] == 'exact':
                hand_args.append(models.Document.meta_provenience == options['document_provenience'])
            elif options['document_provenience_mode'] == 'begins':
                hand_args.append(models.Document.meta_provenience.like(options['document_provenience']+'%'))
            elif options['document_provenience_mode'] == 'contains':
                hand_args.append(models.Document.meta_provenience.like('%'+options['document_provenience']+'%'))
            elif options['document_provenience_mode'] == 'ends':
                hand_args.append(models.Document.meta_provenience.like('%'+options['document_provenience']))
            elif options['document_provenience_mode'] == 'regex':
                hand_args.append(models.Document.meta_provenience.op('regexp')(options['document_provenience']))

        if options['document_date_not_before']:
            hand_args.append(models.Document.meta_date_not_before >= options['document_date_not_before'])
        if options['document_date_not_after']:
            hand_args.append(models.Document.meta_date_not_after <= options['document_date_not_after'])

        or_filters = []
        for handwriting in options['hand_handwriting']:
            or_filters.append(models.Hand.meta_handwriting_professional == handwriting)

        hand_args.append(or_(*or_filters))

        or_filters = []
        for text_type in options['hand_text_type']:
            or_filters.append(models.Hand.meta_text_type == text_type)
        hand_args.append(or_(*or_filters))

        or_filters = []
        for addressee in options['hand_addressee']:
            or_filters.append(models.Hand.meta_addressee == addressee)
        hand_args.append(or_(*or_filters))

        hand_args.append(models.Hand.document_id==models.Document.id)

        hands = Layertreebank.get_filtered(hand_args)

        result_data = []

        for hand in hands:
            standard = ''
            original = ''
            for tb in hand.layertreebanks:

                if tb.type == 'standard':
                    standard = tb.body if tb.body else ''
                elif tb.type == 'original':
                    original = tb.body if tb.body else ''

            if standard and original:

                all_data = {}

                xml_root = etree.fromstring(original)
                all_elements = xml_root.findall(".//*")   

                for element in all_elements:
                    if element.tag.endswith('word'):
                        if 'form' in element.attrib:
                            if query['original']['plain'] == 'true':
                                word_form = ''
                                for c in element.attrib['form']:
                                    word_form += unicodedata.normalize('NFD', c)[0]
                            else:
                                word_form = element.attrib['form']
                            word_print = element.attrib['form']
                        else:
                            word_form = ''
                            word_print = ''
                        if 'lemma' in element.attrib:
                            if query['original']['lemma_plain'] == 'true':
                                lemma_form = ''
                                for c in element.attrib['lemma']:
                                    lemma_form += unicodedata.normalize('NFD', c)[0]
                            else:
                                lemma_form = element.attrib['lemma']
                            lemma_print = element.attrib['lemma']
                        else:
                            lemma_form = ''
                            word_print = ''
                        all_data[int(element.attrib['id'])] = {
                             'word': {
                                'standard': '',
                                'original': word_form,
                            },
                             'word_print': {
                                'standard': '',
                                'original': word_print,
                            },
                            'lemma': {
                                'standard': '',
                                'original': lemma_form,
                            },
                            'lemma_print': {
                                'standard': '',
                                'original': lemma_print,
                            },
                            'relation': {
                                'standard': '',
                                'original': element.attrib['relation'] if 'relation' in element.attrib else '',
                            },
                            'postag': {
                                'standard': '',
                                'original': element.attrib['postag'] if 'postag' in element.attrib else '',
                            },
                        }

                xml_root = etree.fromstring(standard)
                all_elements = xml_root.findall(".//*")   
               
                for i, element in enumerate(all_elements):
                    if element.tag.endswith('word'):
                        if 'form' in element.attrib:
                            if query['standard']['plain'] == 'true':
                                word_form = ''
                                for c in element.attrib['form']:
                                    word_form += unicodedata.normalize('NFD', c)[0]
                            else:
                                word_form = element.attrib['form']
                            word_print = element.attrib['form']
                        else:
                            word_form = ''
                            word_print = ''
                        if 'lemma' in element.attrib:
                            if query['standard']['lemma_plain'] == 'true':
                                lemma_form = ''
                                for c in element.attrib['lemma']:
                                    lemma_form += unicodedata.normalize('NFD', c)[0]
                            else:
                                lemma_form = element.attrib['lemma']
                            lemma_print = element.attrib['lemma']
                        else:
                            lemma_form = ''
                            lemma_print = ''
                        if int(element.attrib['id']) in all_data:
                            all_data[int(element.attrib['id'])]['word']['standard'] = word_form
                            all_data[int(element.attrib['id'])]['word_print']['standard'] = word_print
                            all_data[int(element.attrib['id'])]['lemma']['standard'] = lemma_form
                            all_data[int(element.attrib['id'])]['lemma_print']['standard'] = lemma_print
                            all_data[int(element.attrib['id'])]['relation']['standard'] = element.attrib['relation'] if 'relation' in element.attrib else ''
                            all_data[int(element.attrib['id'])]['postag']['standard'] = element.attrib['postag'] if 'postag' in element.attrib else ''
                        else:
                            all_data[int(element.attrib['id'])] = {
                                 'word': {
                                    'original': '',
                                    'standard': word_form,
                                },
                                 'word_print': {
                                    'original': '',
                                    'standard': word_print,
                                },
                                'lemma': {
                                    'original': '',
                                    'standard': lemma_form,
                                },
                                'lemma_print': {
                                    'original': '',
                                    'standard': lemma_print,
                                },
                                'relation': {
                                    'original': '',
                                    'standard': element.attrib['relation'] if 'relation' in element.attrib else '',
                                },
                                'postag': {
                                    'original': '',
                                    'standard': element.attrib['postag'] if 'postag' in element.attrib else '',
                                },
                            }
                
                keys_to_delete = []
                for i, d in enumerate(all_data):
                    if (query['original']['q'] and not re.search(query['original']['q'], all_data[d]['word']['original'], re.I)) or \
                    (query['original']['lemma'] and not re.search(query['original']['lemma'], all_data[d]['lemma']['original'],  re.I)) or \
                    (query['original']['relation'] and not re.search(query['original']['relation'], all_data[d]['relation']['original'],  re.I)) or \
                    (query['original']['postag'] and not re.search(query['original']['postag'], all_data[d]['postag']['original'], re.I)) or \
                    (query['standard']['q'] and not re.search(query['standard']['q'], all_data[d]['word']['standard'], re.I)) or \
                    (query['standard']['lemma'] and not re.search(query['standard']['lemma'], all_data[d]['lemma']['standard'], re.I)) or \
                    (query['standard']['relation'] and not re.search(query['standard']['relation'], all_data[d]['relation']['standard'], re.I)) or \
                    (query['standard']['postag'] and not re.search(query['standard']['postag'], all_data[d]['postag']['standard'], re.I)):
            

                            keys_to_delete.append(d)

                for k in keys_to_delete:
                    all_data.pop(k, None)

                if all_data:

                    for d in all_data:
                        result_data.append([
                            '<span>'+all_data[d]['word_print']['original']+'</span><span>'+all_data[d]['word_print']['standard']+'</span>',
                            '<span>'+all_data[d]['lemma_print']['original']+'</span><span>'+all_data[d]['lemma_print']['standard']+'</span>',
                            '<span>'+all_data[d]['relation']['original']+'</span><span>'+all_data[d]['relation']['standard']+'</span>',
                            '<span>'+all_data[d]['postag']['original']+'</span><span>'+all_data[d]['postag']['standard']+'</span>',
                            tb.hand.hand_name,
                            tb.hand.document.meta_title
                        ])

                    
        print(query)
        return [result_data]

        
