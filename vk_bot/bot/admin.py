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

import datetime

from vk_bot.bot import bot
from vk_bot import config
from vk_bot.utils import log as logging


CONF = config.CONF
ADMIN_USER_ID = int(CONF.get('auth', 'admin_user_id'))
LOG = logging.getLogger(__name__)
SUB_PARSER = None


def admin_cmd(func):
    def decorator(message, args):
        if message['user_id'] != ADMIN_USER_ID:
            vk_bot = bot.get_bot()

            vk_bot.answer_on_message(
                message,
                "Только админы могут использовать данную команду."
            )
            return

        func(message, args)

    return decorator


def add_admin_namespace(subparser):
    admin = subparser.add_parser(
        'admin',
        help="Группа команд администрирования."
    )
    admin.set_defaults(func=help_message)
    admin_subparsers = admin.add_subparsers(dest='action')

    get_chat_parser = admin_subparsers.add_parser(
        'get-main-chat',
        help="Получить информацию о главном чате."
    )
    get_chat_parser.set_defaults(func=get_main_chat)

    global SUB_PARSER
    if not SUB_PARSER:
        SUB_PARSER = admin


@admin_cmd
def help_message(message, args):
    vk_bot = bot.get_bot()

    cmds = SUB_PARSER._actions[1]

    output = []

    for cmd in cmds.choices:
        output += ["%s:" % cmd]
        output += cmds.choices[cmd].format_help().split('\n')[:-3]
        output += ['']

    vk_bot.answer_on_message(message, '\n'.join(output))


@admin_cmd
def get_main_chat(message, args):
    vk_bot = bot.get_bot()

    chat = vk_bot.main_chat
    chat_id = chat['id']
    chat_name = chat['title']

    last_message = vk_bot.api.messages.getHistory(
        peer_id=2000000000 + int(chat_id),
        count=1,
        user_id=message['user_id'],
        v=5.38
    )['items'][0]

    last_update = datetime.datetime.fromtimestamp(int(last_message['date']))

    vk_bot.answer_on_message(
        message,
        "Main chat: %s. %s, Посл.обновление: %s" % (
            chat_id, chat_name, last_update
        )
    )
