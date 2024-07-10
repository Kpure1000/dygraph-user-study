import logging
from datetime import datetime
import os
import sys

def timenow():
    return datetime.now().strftime('%Y%m%d%H%M%S')

def getLogger(name=None, console_level=logging.DEBUG, file_level=logging.DEBUG):
    os.makedirs(os.path.abspath('logs'), exist_ok=True)
    file_log = os.path.join('logs', f'{name}-{timenow()}.log')
    with open(file_log, 'w') as f:
            pass
    logfile_handler = logging.FileHandler(file_log, mode='a', encoding="utf8")
    logfile_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] TID.%(thread)d %(module)s.%(lineno)d %(name)s:\t%(message)s'))
    logfile_handler.setLevel(file_level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s] %(message)s',datefmt="%Y/%m/%d %H:%M:%S"))
    console_handler.setLevel(console_level)
    logger = logging.getLogger(name)
    logger.addHandler(logfile_handler)
    logger.addHandler(console_handler)
    logger.setLevel(min(console_level, file_level))
    return logger

