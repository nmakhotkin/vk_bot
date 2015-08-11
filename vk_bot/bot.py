# Copyright 2015 - Nikolay Makhotkin.
#
# Licensed under the Whatever You Want License.
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import vk

from vk_bot.auth import auth
from vk_bot import config


CONF = config.CONF
APP_ID = '3756128'
SCOPE = 'messages,friends'
EMAIL = CONF.get('auth', 'email')
PASSWORD = CONF.get('auth', 'password')

MAIN_CHAT_ID = CONF.get('chat', 'main')


def run_test():
    access_token, _ = auth.auth(EMAIL, PASSWORD, APP_ID, SCOPE)
    api = vk.API(access_token=access_token)

    chat = api.messages.getChat(chat_id=MAIN_CHAT_ID)
    if not chat:
        raise Exception("The chat not found for chat id: %s" % MAIN_CHAT_ID)

    api.messages.send(chat_id=chat['id'], message='VkBot test')
