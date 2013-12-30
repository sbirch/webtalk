import logging
import sys

LOG_LVL = logging.DEBUG
LOG_FILE = sys.stderr

logging.basicConfig(stream=LOG_FILE,level=LOG_LVL, format='%(filename)s.%(lineno)s:%(levelname)s: %(message)s')

# tell selenium to shut up
se_logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
se_logger.setLevel(logging.WARNING)
