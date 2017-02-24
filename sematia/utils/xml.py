import os
import re
import sys
import traceback
import urllib.request
import xml.etree.ElementTree as etree

from ..models import db, User, Document, Hand, Layertreebank
from .. import app
from . import log

log = log.Log

class Xml():
    xmlstr = ''

    @staticmethod
    def validate(xml):
        try:
            doc = etree.fromstring(xml)
            return doc
        except:
            return False


    @classmethod
    def convert_element(cls, element, depth):
        if type(element.tag) is str:
            tag = element.tag
            text = element.text if element.text is not None else ''
            tail = element.tail if element.tail is not None else ''
            attr = element.attrib if element.attrib is not None else {}

            # Strip newlines
            text = re.sub(r"\n", "", text)
            tail = re.sub(r"\n", "", tail)

            attributes = ""
            for key, value in attr.items():
                attributes += 'data-'+key+"='"+value+"'"

            cls.xmlstr += '<span class="'+tag+'" '+attributes+'>'

            if text != '':
                cls.xmlstr += '<span class="text">'+text+'</span>'

            return tail

    @classmethod
    def convert_transcription(cls, node, depth=0):
        elements = node.findall('*') or []
        for element in elements:
            tail = Xml.convert_element(element, depth)
            Xml.convert_transcription(element, depth+1)
            if tail:
                cls.xmlstr += '<span class="text tail">'+tail+'</span>'
        cls.xmlstr += '</span>'

    @classmethod
    def to_html(cls, xml):
        cls.xmlstr = ''
        try:
            doc = etree.fromstring(xml).find('.//*[@type="edition"]')
            Xml.convert_transcription(doc)
        except Exception:
            log.e()
            return False 

        return cls.xmlstr

    @staticmethod
    def get_hand_names_temp(xml):
        hands = ['m1']

        xml_root = etree.fromstring(xml)
        all_elements = xml_root.findall(".//*")   

        for element in all_elements:
            if element.tag.endswith('handShift'):
                hands.append(element.attrib['new'])

        return hands

    @staticmethod
    def get_metadata(xml):
        special_dates = app.app.config['DATE_STRINGS']
        dates_not_before = []
        dates_not_after = []
        place = ''
        title = ''
        date_not_before = ''
        date_not_after = ''
        hands = ['m1']

        xml_root = etree.fromstring(xml)
        title = xml_root.find('.//titleStmt/title').text
        if not title:
            title = ''.join(xml_root.find('.//titleStmt/title').itertext())

        all_elements = xml_root.findall(".//*")   

        for element in all_elements:
            if element.tag.endswith('handShift'):
                hands.append(element.attrib['new'])
            if element.tag.endswith('date'):
                date = element.text
                if date in special_dates:
                    if special_dates[date][0] != '':
                        proposed_date = int(special_dates[date][0])
                        if not dates_not_before or proposed_date < min(dates_not_before):
                            dates_not_before.append(proposed_date)
                    if special_dates[date][1] != '':
                        proposed_date = int(special_dates[date][1])
                        if not dates_not_after or proposed_date > max(dates_not_after):
                            dates_not_after.append(proposed_date)
            elif element.tag.endswith('placeName'):
                place = element.text
        if xml_root.findall(".//*[@type='HGV']"):
            hgv_id = xml_root.findall(".//*[@type='HGV']")[0].text.split()[0]
            if hgv_id:
                url = 'http://papyri.info/hgv/'+hgv_id+'/source'
                with urllib.request.urlopen(url) as url:
                    s = url.read()
                hgv_tree = etree.fromstring(s)
                hgv_elements = hgv_tree.findall(".//*") 
                
                for hgv_el in hgv_elements:     
                    if hgv_el.tag.endswith('origDate'):
                    
                        for items in hgv_el.items():
                            if items[0] == 'when' \
                                or items[0] == 'notBefore' \
                                or items[0] == 'notAfter':

                                proposed_date = ''

                                if items[1].startswith('-'):
                                    proposed_date = '-'+items[1] \
                                        .split('-')[1]
                                else:
                                    proposed_date = items[1] \
                                        .split('-')[0]

                                if proposed_date != '':

                                    proposed_date = int(proposed_date)

                                    if items[0] == 'when':
                                        if not dates_not_before or proposed_date < min(dates_not_before):
                                            dates_not_before.append(proposed_date)
                                        if not dates_not_after or proposed_date > max(dates_not_after):
                                            dates_not_after.append(proposed_date)
                                    elif items[0] == 'notBefore':
                                        if not dates_not_before or proposed_date < min(dates_not_before):
                                            dates_not_before.append(proposed_date)
                                    else:
                                        if not dates_not_after or proposed_date > max(dates_not_after):
                                            dates_not_after.append(proposed_date)
                    
                    elif hgv_el.tag.endswith('origPlace'):
                        place = hgv_el.text


        # Remove empty entries
        dates_not_before = list(filter(None, dates_not_before))
        dates_not_after = list(filter(None, dates_not_after))

        if dates_not_before:
            date_not_before = min(dates_not_before)
        if dates_not_after:
            date_not_after = max(dates_not_after)

        place = place.strip() if place else ''

        return {
            'title': title,
            'hands': hands,
            'date_not_before': date_not_before,
            'date_not_after': date_not_after,
            'provenience': place
        }

    @staticmethod
    def start(xml):
        try:
            xml_no_ns = xml.replace(' xmlns="', ' xmlnsBackup="')
            html = Xml.to_html(xml_no_ns)
            if html:
                metadata = Xml.get_metadata(xml_no_ns)
                return {'status': 'ok', 
                        'html': html,
                        'title': metadata['title'],
                        'hands': metadata['hands'],
                        'date_not_before': metadata['date_not_before'],
                        'date_not_after': metadata['date_not_after'],
                        'provenience': metadata['provenience']
                }
            else:
                return {'status': 'error', 'message':'Parsing error.'}

        except Exception:
            log.e()
            return {'status': 'error', 'message':'Parsing error.'}   

    @staticmethod
    def count_words(xml):
        count = 0
        xml_root = etree.fromstring(xml)
        all_elements = xml_root.findall(".//*")   

        for element in all_elements:
            if element.tag.endswith('word') and 'artificial' not in element.attrib:
                count += 1

        return count