# -*- coding: utf-8 -*-

import os
import difflib
import re
import xml.etree.ElementTree as etree
import fnmatch
import traceback

from datetime import datetime

from flask import session, jsonify

from ..models import db, User, Document, Hand, Layertreebank
from ..utils import records


class Edit():

    model_map = {
        'User':User,
        'Document':Document,
        'Hand':Hand,
        'Layertreebank':Layertreebank
    }

    @classmethod
    def get(cls, model, id):
        model = cls.model_map[model]
        return model.query.get(id)