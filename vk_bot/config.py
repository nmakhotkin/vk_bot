
from six.moves import configparser

from vk_bot import utils


_ACCOUNT_FILE = '../account.conf'
CONF = None


def parse():
    config = configparser.RawConfigParser()

    global CONF
    if not CONF and config.read(utils.get_file_path(_ACCOUNT_FILE)):
        CONF = config
