
import configparser

from vk_bot.utils import file_utils


_ACCOUNT_FILE = '../bot.conf'
CONF = None


def parse():
    config = configparser.ConfigParser()
    global CONF
    if not CONF and config.read(file_utils.get_file_path(_ACCOUNT_FILE)):
        CONF = config


def write():
    with open('bot.conf', 'w') as fp:
        CONF.write(fp)
