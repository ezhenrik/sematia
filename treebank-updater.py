import sys
import os
import glob
from datetime import datetime
import xml.etree.ElementTree as etree
import logging

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from config import VENV_PATH

sys.path.append(VENV_PATH + '/lib/python3.5/site-packages')

from sematia import app

app = app.app

from sematia import models
from sematia.utils import log
db = models.db
db.init_app(app)
Log = log.Log

app.config.from_object('config')

if app.config['LOG']:
    logging.basicConfig(filename=app.config['LOGFILE'], level=logging.DEBUG)

with app.app_context():

    for filename in glob.iglob(app.config['TB_REPO']+'/**/*.xml', recursive=True):
        f = open(filename, 'r')
        xml = f.read()
        xml_root = etree.fromstring(xml)
        all_elements = xml_root.findall(".//*") 
        tb_id = False
        for element in all_elements:
            if element.tag.endswith('sentence'):
                if 'document_id' in element.attrib:
                    tb_id = element.attrib['document_id'].rsplit('/', 1)[-1]
                    break

        if tb_id:
            try:
                layertreebank = models.Layertreebank.query.get(tb_id)
                if layertreebank:
                    layertreebank.approved_user_id = 2
                    layertreebank.body = xml
                    layertreebank.updated = datetime.today()
                    db.session.commit()
                else:
                    Log.p('No layertreebank '+tb_id)
            except Exception:
                Log.e()
        else:
            Log.p('No tb_id for file '+filename)
