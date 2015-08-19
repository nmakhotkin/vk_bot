# Copyright 2015 - Nikolay Makhotkin.
#
# Licensed under the Whatever You Want License.
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging

import requests
import urllib
import urlparse
import vk

from vk_bot import config
from vk_bot import utils

LOG = logging.getLogger(__name__)
CONF = config.CONF

MAIN_CHAT_ID = CONF.get('chat', 'main')
BOT = None


def get_bot():
    global BOT

    if not BOT:
        app_id = CONF.get('auth', 'app_id')
        scope = 'messages,friends,photos'
        email = CONF.get('auth', 'email')
        password = CONF.get('auth', 'password')

        BOT = VkBot(email, password, app_id, scope)

    return BOT


class VkBot(object):
    def __init__(self, email, password, app_id, scope):
        self.app_id = app_id

        self._api = vk.OAuthAPI(
            app_id=app_id,
            user_login=email,
            user_password=password,
            scope=scope
        )
        self._main_chat = None

    @property
    def api(self):
        if not self._api.access_token:
            self._api.get_access_token()
        return self._api

    @property
    def main_chat(self):
        if not self._main_chat:
            chat = self.api.messages.getChat(chat_id=MAIN_CHAT_ID)

            if not chat:
                raise Exception(
                    "The chat not found for chat id: %s" % MAIN_CHAT_ID
                )

            self._main_chat = chat

        return self._main_chat

    def send_to_main(self, message):
        return self.api.messages.send(
            chat_id=self.main_chat['id'],
            message=message
        )

    def send_to_main_picture(self, picture_url, message=None):
        photo_id = self._get_photo_id(picture_url)

        params = {
            'attachment': photo_id,
            'chat_id': self.main_chat['id']
        }

        if message:
            params.update({'message': message})

        return self.api.messages.send(**params)

    @utils.with_retry()
    def _get_server_url(self):
        server_url = self.api.photos.getMessagesUploadServer()
        return server_url['upload_url']

    def _get_photo_id(self, photo_url):
        server_url = self._get_server_url()

        photo, resp = urllib.urlretrieve(photo_url)

        data = {}
        files = {'photo': (photo, open(photo, 'rb'))}
        url = server_url.split('?')[0]
        for key, value in urlparse.parse_qs(server_url.split('?')[1]).iteritems():
            data[key] = value

        resp = requests.post(url, data, files=files)

        if not resp.json().get('photo'):
            raise RuntimeError("The photo is not uploaded properly.")

        params = {
            'server': resp.json()['server'],
            'photo': [resp.json()['photo']],
            'hash': [resp.json()['hash']]
        }
        photo_info = self.api.photos.saveMessagesPhoto(**params)

        return "photo%s_%s" % (photo_info[0]['owner_id'], photo_info[0]['id'])

    def test(self):
        LOG.info("Sending test info...")

        self.send_to_main(
            'VkBot Test. This is automatically constructed message.'
        )

        LOG.info("Sent.")
