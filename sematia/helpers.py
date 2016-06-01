import os
import re
import sys
import traceback
import urllib

from db import db
from flask import session
from lxml import etree as lxmletree
import xml.etree.ElementTree as etree

from models import Document, Hand, Layertreebank, User
from app import app

class XmlHelpers():
    tags = []
    xmlstr = ''

    @classmethod
    def getElement(self, element, depth):
        if type(element.tag) is str:
            tag = element.tag
            text = element.text if element.text is not None else ''
            tail = element.tail if element.tail is not None else ''
            attr = element.attrib if element.attrib is not None else {}

            # Strip newlines
            text = re.sub(r"\n", "", text)
            tail = re.sub(r"\n", "", tail)

            attributes = ""
            for key, value in attr.iteritems():
                attributes += 'data-'+key+"='"+value+"'"

            self.xmlstr += '<span class="'+tag+'" '+attributes+'>'

            if text != '':
                self.xmlstr += '<span class="text">'+text+'</span>'

            return tail

    @classmethod
    def findElements(self, node, depth=0, tags=[], xmlstr=''):
        elements = node.findall('*') or []
        for element in elements:
            tail = XmlHelpers.getElement(element, depth)
            XmlHelpers.findElements(element, depth+1)
            if tail != '':
                self.xmlstr += '<span class="text tail">'+tail+'</span>'
        self.xmlstr += '</span>'

    @classmethod
    def convertToHtml(self, xml):
        self.xmlstr = ''
        try:
            doc = etree.fromstring(xml).find('.//*[@type="edition"]')
            XmlHelpers.findElements(doc)
        except Exception as e:
            app.logger.error(traceback.format_exc())
            return False 

        return self.xmlstr

    @staticmethod
    def importDocument(url):
        try:
            f = urllib.urlopen(url)
            xml = f.read()
        except Exception:
            app.logger.error(traceback.format_exc())
            return {'status': 'error', 
                    'message':'Could not open the source URL.'} 
        try:
            # Remove namespaces
            strippedXml = xml.replace(' xmlns="', ' xmlnsBackup="')
            tree = etree.fromstring(strippedXml)
            hands = len(tree.findall('.//handShift')) + 1
            title = tree.find('.//titleStmt/title').text
            html = XmlHelpers.convertToHtml(strippedXml)
            if not html:
                raise ValueError('Could not convert to HTML')
            return {'status':'ok', 'title':title, 'xml':xml, 
                    'html':html, 'hands':hands}

        except Exception:
            app.logger.error(traceback.format_exc())
            return {'status': 'error', 'message':'Parsing error.'}   

class DbHelpers():

    @staticmethod
    def own(model, id):
        try:
            if str(id).isdigit:
                if model is 'Document':
                    return Document.query.filter_by(
                        id=id, user_id=session['user_id']).first()
                elif model is 'Hand':
                    # Subquery: get user documents
                    document_sub = db.session.query(Document.id) \
                        .filter(Document.user_id==session['user_id']).subquery()
                    return db.session.query(Hand) \
                        .join(document_sub, document_sub.c.id==Hand.document_id) \
                        .filter(Hand.id==id).first()
                elif model is 'Layertreebank':
                    # Subquery: get user documents
                    document_sub = db.session.query(Document.id) \
                        .filter(Document.user_id==session['user_id']).subquery()
                    print (db.session.query(Document.id) \
                        .filter(Document.user_id==session['user_id']).first())
                    # Subquery: get document hands
                    hand_sub = db.session.query(Hand.id) \
                        .join(document_sub, document_sub.c.id==Hand.document_id) \
                        .subquery()
                    # Get hand layers
                    return db.session.query(Layertreebank) \
                    .join(hand_sub, hand_sub.c.id==Layertreebank.hand_id) \
                    .filter(Layertreebank.id==id).first()
                else: 
                    return None
            else:
                return None
        except Exception:
            print str(traceback.format_exc())
            return None

