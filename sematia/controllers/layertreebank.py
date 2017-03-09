import zipfile
import io
import time
import xml.etree.ElementTree as etree

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
                        
                        all_data[int(element.attrib['id'])] = {
                             'word': {
                                'standard': '',
                                'original': element.attrib['form'] if 'form' in element.attrib else '',
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
                        if int(element.attrib['id']) in all_data:
                            print('oli')

                            all_data[int(element.attrib['id'])]['word']['standard'] = element.attrib['form'] if 'form' in element.attrib else ''
                            all_data[int(element.attrib['id'])]['relation']['standard'] = element.attrib['relation'] if 'relation' in element.attrib else ''
                            all_data[int(element.attrib['id'])]['postag']['standard'] = element.attrib['postag'] if 'postag' in element.attrib else ''
                        '''else:
                            all_data[int(element.attrib['id'])] = {
                                 'word': {
                                    'original': '',
                                    'standard': element.attrib['form'] if 'form' in element.attrib else '',
                                },
                                'relation': {
                                    'original': '',
                                    'standard': element.attrib['relation'] if 'relation' in element.attrib else '',
                                },
                                'postag': {
                                    'original': '',
                                    'standard': element.attrib['postag'] if 'postag' in element.attrib else '',
                                },
                            }'''
                
                keys_to_delete = []
                for i, d in enumerate(all_data):
                    if (query['original']['q'] and all_data[d]['word']['original'].lower() != query['original']['q'].lower()) or \
                    (query['original']['relation'] and all_data[d]['relation']['original'].lower() != query['original']['relation'].lower()) or \
                    (query['original']['postag'] and all_data[d]['postag']['original'].lower() != query['original']['postag'].lower()) or \
                    (query['standard']['q'] and all_data[d]['word']['standard'].lower() != query['standard']['q'].lower()) or \
                    (query['standard']['relation'] and all_data[d]['relation']['standard'].lower() != query['standard']['relation'].lower()) or \
                    (query['standard']['postag'] and all_data[d]['postag']['standard'].lower() != query['standard']['postag'].lower()):

                            keys_to_delete.append(d)

                for k in keys_to_delete:
                    all_data.pop(k, None)

                if all_data:

                    for d in all_data:
                        result_data.append([
                            all_data[d]['word']['original']+' | '+all_data[d]['word']['standard'],
                            all_data[d]['relation']['original']+' | '+all_data[d]['relation']['standard'],
                            all_data[d]['postag']['original']+' | '+all_data[d]['postag']['standard'],
                            tb.hand.id
                        ])

                    

        return [result_data]




        '''
        dates_null_before = 'or doc.date_not_before is null' \
            if options['dates_null_before'] == 'false' else ''
        dates_null_after = 'or doc.date_not_after is null' \
            if options['dates_null_after'] == 'false' else ''
        sql_where = ' where (op.name = "'+options["mode"]+'")'
        sql_where += ' and (convert(doc.date_not_after, signed int) <= "'+options['date_not_after']+'" \
                            '+dates_null_after+') \
                       and (convert(doc.date_not_before, signed int) >= "'+options['date_not_before']+'" \
                           '+dates_null_before+')' 
        if options["series"]:
            sql_where += ' and ('
            for i, serie in enumerate(options['series']):
                sql_where += ' collection.name = "'+serie+'"'
                if i < len(options["series"])-1:
                    sql_where += ' or '
            sql_where += ') '
        for key, val in query.items():
            if query[key]['q'] != '' or query[key]['mode'] == 'empty':
                if query[key]['mode'] == 'empty':
                    sql_where += 'and ('+key+'_t.string is null '
                else:
                    sql_where += 'and ('+key+'_t.string '
                    if query[key]['mode'] == 'exact':
                        sql_where += '= "'+query[key]['q']+'"'
                    elif query[key]['mode'] == 'begins':
                        sql_where += 'like "'+query[key]['q']+'%%"'
                    elif query[key]['mode'] == 'contains':
                        sql_where += 'like "%%'+query[key]['q']+'%%"'
                    elif query[key]['mode'] == 'ends':
                        sql_where += 'like "%%'+query[key]['q']+'"'
                    elif query[key]['mode'] == 'regex':
                        sql_where += 'regexp "'+query[key]['q']+'"'

                    if query[key]['plain'] == 'false':
                        sql_where += ' collate utf8mb4_bin'

                sql_where += ") "

        sql = 'select op.name as mode, \
               doc.name as filename, \
               doc.date_not_after as dna, \
               doc.date_not_before as dnb, \
               path.path as path, \
               place.name as place, \
               place.pid as pid, \
               collection.name as collection, \
               element.name as element, \
               variation.pos as position, \
               coalesce(orig_t.string, "") as orig, \
               coalesce(orig_before_t.string, "") as orig_before, \
               coalesce(orig_after_t.string, "") as orig_after, \
               coalesce(stan_t.string, "") as stan, \
               coalesce(stan_before_t.string, "") as stan_before, \
               coalesce(stan_after_t.string, "") as stan_after \
               from '+prefix+'variation as variation \
               left join '+prefix+'operation as op on op.id=variation.operation_id \
               left join '+prefix+'document as doc on doc.id=variation.doc_id \
               left join '+prefix+'path as path on doc.path_id=path.id \
               left join '+prefix+'collection as collection on doc.collection_id=collection.id \
               left join '+prefix+'element as element on variation.element_id=element.id \
               left join '+prefix+'place as place on doc.place_id=place.id \
               left join '+prefix+'text as orig_t on orig_t.id=variation.orig_id \
               left join '+prefix+'text as orig_before_t on orig_before_t.id=variation.orig_before_id \
               left join '+prefix+'text as orig_after_t on orig_after_t.id=variation.orig_after_id \
               left join '+prefix+'text as stan_t on stan_t.id=variation.stan_id \
               left join '+prefix+'text as stan_before_t on stan_before_t.id=variation.stan_before_id \
               left join '+prefix+'text as stan_after_t on stan_after_t.id=variation.stan_after_id \
               ' + sql_where
        try:
            result = db.engine.execute(sql)
        except Exception as e:
            app.app.logger.error(traceback.format_exc())
            return 'false'


        retval = []
        pid_places = {}
        no_pids = {}

        for row in result:

            rowplain = []
            rowdict = dict(zip(row.keys(), row))

            explanation = ''
            if rowdict['pid']:
                pid = str(rowdict['pid'])

                if pid not in pid_places:
                    pid_places[pid] = {'dnb': float('inf'), 'dna': float('-inf')}
                    pid_places[pid]['place'] = rowdict['place']
                    pid_places[pid]['amount'] = 1
                else:
                    pid_places[pid]['amount'] += 1

                if rowdict['dnb']:
                    if not pid_places[pid]['dnb'] or (pid_places[pid]['dnb'] and int(rowdict['dnb']) < pid_places[pid]['dnb']):
                        pid_places[pid]['dnb'] = int(rowdict['dnb'])

                if rowdict['dna']:
                    if not pid_places[pid]['dna'] or (pid_places[pid]['dna'] and int(rowdict['dna']) > pid_places[pid]['dna']):
                        pid_places[pid]['dna'] = int(rowdict['dna'])
              
            else:
                if rowdict['place'] in no_pids:
                    no_pids[rowdict['place']] += 1
                else:
                    no_pids[rowdict['place']] = 1
            if rowdict['mode'] == 'delete':
                explanation = '<strong class="red">- '+ rowdict['orig']+'</strong>'
            elif rowdict['mode'] == 'insert':
                explanation = '<strong class="green">+ '+ rowdict['stan']+'</strong>'
            elif rowdict['mode'] == 'replace':
                explanation = '<strong class="red">- '+ rowdict['orig']+'</strong> <strong class="green">+ '+rowdict['stan']+'</strong>'
            stafter = rowdict['stan_after'][len(rowdict['stan']):] if experimental else rowdict['stan_after']
            rowplain.extend(
                (rowdict['orig_before']+'<strong class="red">'+rowdict['orig']+'</strong>' \
                    +rowdict['orig_after'],
                 rowdict['stan_before']+'<strong class="green">'+rowdict['stan']+'</strong>' \
                    +stafter,

                 explanation,
                 rowdict['dnb'],
                 rowdict['dna'],
                 rowdict['place'],
                 '<span class="meta filename badge">'+str(rowdict['filename'])[:-4]+' <i class="fa fa-external-link-square"></i></span>'+ \
                 '<span class="meta position badge">'+str(rowdict['position'])+'</span>')
                )
            retval.append(rowplain)

        locs = []
        types_map =  {
            '1': 'Point',
            '2': 'LineString',
            '3': 'Polygon',
            '4': 'MultiPoint',
            '5': 'MultiLineString',
            '6': 'MultiPolygon',
            '7': 'GeometryCollection'
        }
        max_date = ''
        min_date = ''
        if pid_places:
            max_value = pid_places[max(pid_places, key=lambda x: pid_places[x]['amount'])]['amount']
            max_date = pid_places[max(pid_places, key=lambda x: pid_places[x]['dna'])]['dna']
            min_date = pid_places[max(pid_places, key=lambda x: pid_places[x]['dnb'])]['dnb']


        max_color = 255

        if not max_date or math.isinf(max_date):
            max_date = 1000

        if not min_date or math.isinf(min_date):
            min_date = -500



        for pid in pid_places:
            loc = Location.query.filter_by(pid=pid).first()
            amount = round(float(pid_places[pid]['amount'])/float(max_value), 2)
            dna = 0 if not pid_places[pid]['dna'] or math.isinf(pid_places[pid]['dna']) else pid_places[pid]['dna']
            dnb = 0 if not pid_places[pid]['dnb'] or math.isinf(pid_places[pid]['dnb']) else pid_places[pid]['dnb']

            color = 0

            div = 2 if dna and dnb else 1

            color = round((float(abs(min_date)) + dnb+dna / float(div)) / float(abs(min_date + max_date)) * 255, 0)

            if not dna:
                dna = 'unknown'

            if not dnb:
                dnb = 'unknown'

            if loc:
                locs.append({'type': types_map[str(loc.coord_type)], 'coordinates':json.loads(loc.coordinates), 'properties':{'dna': dna, 'dnb': dnb, 'realamount': pid_places[pid]['amount'], 'amount':amount, 'place':pid_places[pid]['place'], 'color': color}})

        pid_ratio = 'Pleiades data: '+str(len(locs))+' of '+str(len(no_pids)+len(locs))+' places'


        return [retval, locs, pid_ratio]
    '''
        
