import logging
from logging.handlers import RotatingFileHandler
import sys 
# LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FORMAT = '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s' #FUNC
formatter = logging.Formatter(LOG_FORMAT)


fh = logging.FileHandler('test.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

file_handler = RotatingFileHandler('info.log', maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.INFO)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))


