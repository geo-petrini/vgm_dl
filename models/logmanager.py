import os
import logging
import logging.handlers

FILE_INFO_HANDLER = 'FILE_INFO_HANDLER'
FILE_DEBUG_HANDLER = 'FILE_DEBUG_HANDLER'
CONSOLE_DEBUG_HANDLER = 'CONSOLE_DEBUG_HANDLER'


def get_configured_logger(name=None, outpath='.', handlers=[FILE_INFO_HANDLER, FILE_DEBUG_HANDLER, CONSOLE_DEBUG_HANDLER]):
    logger = logging.getLogger(name) if name != None else logging.getLogger()
    if (len(logger.handlers) == 0):

        outpath = '.' if outpath == None else outpath
        if not os.path.exists(outpath):
            os.mkdir(outpath)
       
        formatter = "%(asctime)s %(levelname)s %(process)s %(thread)s %(filename)s %(funcName)s():%(lineno)d %(message)s"
        
        if isinstance(handlers, str):
            handlers = handlers.split(',')

        if isinstance(handlers, list) and len(handlers) > 0:
            if FILE_INFO_HANDLER in handlers:
                fhandler = logging.handlers.RotatingFileHandler(os.path.join(
                    outpath, 'app.log'), maxBytes=1024*1024*10, backupCount=6)
                fhandler.setFormatter(logging.Formatter(formatter))
                fhandler.setLevel(logging.INFO)
                logger.addHandler(fhandler)

            if FILE_DEBUG_HANDLER in handlers:
                fhandler_d = logging.handlers.RotatingFileHandler(os.path.join(
                    outpath, 'app_debug.log'), maxBytes=1024*1024*10, backupCount=2)
                fhandler_d.setFormatter(logging.Formatter(formatter))
                fhandler_d.setLevel(logging.DEBUG)
                logger.addHandler(fhandler_d)

            if CONSOLE_DEBUG_HANDLER in handlers:
                chandler = logging.StreamHandler()
                chandler.setFormatter(logging.Formatter(formatter))
                chandler.setLevel(logging.DEBUG)
                logger.addHandler(chandler)

            logger.setLevel(logging.DEBUG)
    else:
        pass
    return logger
