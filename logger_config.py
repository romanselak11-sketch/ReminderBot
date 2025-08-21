import logging
import os
from datetime import datetime

dir_log = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(dir_log, exist_ok=True)

log_date = datetime.now().strftime('%d.%m.%Y')
log_file = os.path.join(dir_log, f'{log_date}.log')


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file, encoding='utf-8')])

def get_logger(name: str):
    return logging.getLogger(name)

