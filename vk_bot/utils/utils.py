# coding=utf-8
# Copyright 2015 - Nikolay Makhotkin.
#
# Licensed under the Whatever You Want License.
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from bs4 import BeautifulSoup
import datetime
from eventlet import corolocal
from eventlet import semaphore
import imghdr
import requests
import shutil
import sys
import threading
import time
import traceback

from croniter import croniter

try:
    from urllib import parse as urlparse
    from urllib import request as download
except ImportError:
    import urllib as download
    import urlparse

from vk_bot.utils import log as logging


# Thread local storage.
_th_loc_storage = threading.local()


SEMAPHORES = {}
LOG = logging.getLogger(__name__)


def _get_greenlet_local_storage():
    greenlet_id = corolocal.get_ident()

    greenlet_locals = getattr(_th_loc_storage, "greenlet_locals", None)

    if not greenlet_locals:
        greenlet_locals = {}
        _th_loc_storage.greenlet_locals = greenlet_locals

    if greenlet_id in greenlet_locals:
        return greenlet_locals[greenlet_id]
    else:
        return None


def has_thread_local(var_name):
    gl_storage = _get_greenlet_local_storage()
    return gl_storage and var_name in gl_storage


def get_thread_local(var_name):
    if not has_thread_local(var_name):
        return None

    return _get_greenlet_local_storage()[var_name]


def set_thread_local(var_name, val):
    if not val and has_thread_local(var_name):
        gl_storage = _get_greenlet_local_storage()

        # Delete variable from greenlet local storage.
        if gl_storage:
            del gl_storage[var_name]

        # Delete the entire greenlet local storage from thread local storage.
        if gl_storage and len(gl_storage) == 0:
            del _th_loc_storage.greenlet_locals[corolocal.get_ident()]

    if val:
        gl_storage = _get_greenlet_local_storage()
        if not gl_storage:
            gl_storage = _th_loc_storage.greenlet_locals[
                corolocal.get_ident()] = {}

        gl_storage[var_name] = val


def get_next_time(pattern, start_time=None):
    if not start_time:
        start_time = datetime.datetime.now()

    return croniter(pattern, start_time).get_next(datetime.datetime)


def add_semaphore(key, thread_num):
    SEMAPHORES[key] = semaphore.Semaphore(thread_num)


def remove_semaphore(key):
    del SEMAPHORES[key]


def with_retry(count=3, delay=1, accept_none=False):
    def decorator(func):
        def wrapped(*args, **kwargs):
            counter = 0

            while counter <= count:
                try:
                    result = func(*args, **kwargs)
                    if not accept_none and not result:
                        raise Exception("The function returns None.")

                    return result
                except Exception:
                    formatted = traceback.format_exc()
                    LOG.warn("Retry got error: %s" % formatted)

                    counter += 1
                    time.sleep(delay)

            raise RuntimeError("The function is failed to execute.")
        return wrapped
    return decorator


def download_file(url):
    file_path, _ = download.urlretrieve(url)

    if '.' not in file_path:
        extension = imghdr.what(file_path)

        if not extension:
            extension = 'png'

        shutil.move(file_path, '%s.%s' % (file_path, extension))
        file_path += '.%s' % extension

    return file_path


def get_dollar_info():
    url = 'http://kursnazavtra.info/'
    resp = requests.get(url)

    parsed_html = BeautifulSoup(resp.content, "html5lib")
    tags = parsed_html.findAll('div', attrs={'class': 'style1'})

    return {
        'today': tags[0].text,
        'tomorrow': tags[1].text
    }


def get_euro_info():
    url = 'http://kursnazavtra.info/'
    resp = requests.get(url)

    parsed_html = BeautifulSoup(resp.content, "html5lib")
    tags = parsed_html.findAll('div', attrs={'class': 'style1'})

    return {
        'today': tags[2].text,
        'tomorrow': tags[3].text
    }


def upload_file_on_server(server_url, file_url, entity_type='photo'):
    file_path = download_file(file_url)

    data = {}
    files = {entity_type: (file_path, open(file_path, 'rb'))}
    url = server_url.split('?')[0]
    parsed_qs = urlparse.parse_qs(server_url.split('?')[1])
    for key, value in parsed_qs.items():
        data[key] = value

    resp = requests.post(url, data, files=files)

    if resp.status_code not in range(200, 399):
        raise RuntimeError("Request is unsuccessful: %s" % resp.content)

    if not resp.json().get(entity_type):
        raise RuntimeError(
            "The %s is not uploaded properly: %s"
            % (entity_type, resp.content)
        )

    return resp.json()


def import_class(import_str):
    """Returns a class from a string including module and class."""
    mod_str, _sep, class_str = import_str.rpartition('.')
    __import__(mod_str)
    try:
        return getattr(sys.modules[mod_str], class_str)
    except AttributeError:
        raise ImportError('Class %s cannot be found (%s)' %
                          (class_str,
                           traceback.format_exception(*sys.exc_info())))


def log_execution(message_before, message_after, message_exc=None):
    def decorator(func):
        def wrapped(*args, **kwargs):
            LOG.info(message_before)

            try:
                result = func(*args, **kwargs)

                LOG.info(message_after)

                return result
            except Exception:
                formatted = traceback.format_exception(*sys.exc_info())
                if not message_exc:
                    LOG.warn(formatted)
                else:
                    LOG.warn("%s:" % message_exc)
                    LOG.exception(formatted)

        return wrapped
    return decorator
