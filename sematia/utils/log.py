import traceback

from .. import app

class Log():

    @staticmethod
    def e():
        app.app.logger.error(traceback.format_exc())
