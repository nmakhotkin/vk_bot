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

import vk

from vk_bot import config

LOG = logging.getLogger(__name__)
CONF = config.CONF

MAIN_CHAT_ID = CONF.get('chat', 'main')
BOT = None


def get_bot():
    global BOT

    if not BOT:
        app_id = CONF.get('auth', 'app_id')
        scope = 'messages,friends,photo'
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

    def _get_photo_id(self, photo_url):
        # TODO(nmakhotkin): complete the method.
        # server_url = self.api.photos.getMessagesUploadServer()['upolad_url']

        # photo, resp = urllib.urlretrieve(photo_url)

        # requests.post(server_url, photo)
        pass

    def test(self):
        LOG.info("Sending test info...")

        self.send_to_main(
            'VkBot Test. This is automatically constructed message.'
        )

        LOG.info("Sent.")
