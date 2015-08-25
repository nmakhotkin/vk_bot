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

import BeautifulSoup
from eventlet import corolocal
import requests
import shutil
import threading
import time
import urllib

from vk_bot.utils import log as logging


# Thread local storage.
_th_loc_storage = threading.local()


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
                except Exception as e:
                    LOG.exception("Retry got error: %s" % e)

                    counter += 1
                    time.sleep(delay)

            raise RuntimeError("The function is failed to execute.")
        return wrapped
    return decorator


def download_picture(url):
    file_path, _ = urllib.urlretrieve(url)

    if '.' not in file_path:
        shutil.move(file_path, '%s.png' % file_path)
        file_path += '.png'

    return file_path


def get_dollar_info():
    url = 'http://kursnazavtra.info/'
    resp = requests.get(url)

    parsed_html = BeautifulSoup.BeautifulSoup(resp.content)
    tags = parsed_html.findAll('div', attrs={'class': 'style1'})

    return {
        'today': tags[0].text,
        'tomorrow': tags[1].text
    }


def log_execution(message_before, message_after, message_exc=None):
    def decorator(func):
        def wrapped(*args, **kwargs):
            LOG.info(message_before)

            try:
                result = func(*args, **kwargs)

                LOG.info(message_after)

                return result
            except Exception as e:
                if not message_exc:
                    LOG.warn(str(e))
                else:
                    LOG.warn("%s:\n%s" % (message_exc, e))

        return wrapped
    return decorator
