
from six.moves import configparser

from vk_bot.utils import file_utils


_ACCOUNT_FILE = '../account.conf'
CONF = None


def parse():
    config = configparser.RawConfigParser()

    global CONF
    if not CONF and config.read(file_utils.get_file_path(_ACCOUNT_FILE)):
        CONF = config
