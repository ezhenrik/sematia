import traceback
import datetime

from .. import app

class Log():

    @staticmethod
    def e():
        app.app.logger.error(traceback.format_exc())

    @staticmethod
    def p(text):
        app.app.logger.info(text)
