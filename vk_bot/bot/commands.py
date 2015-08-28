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

import argparse

from vk_bot.bot import bot
from vk_bot import version


class ArgumentParserError(Exception):
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)


def execute_cmd(message, command):
    parser = get_parser()

    args = parser.parse_args(command.split(' '))

    return args.func(message, args)


def get_parser():
    global_parser = ThrowingArgumentParser(
        'bot',
        version=version.version_string
    )

    subparser = global_parser.add_subparsers()

    parser = subparser.add_parser('bot')
    subparser = parser.add_subparsers()

    parser = subparser.add_parser('hello')
    parser.add_argument(
        '-private',
        action='store_true',
        dest='private'
    )
    parser.set_defaults(func=hello)

    return global_parser


def hello(message, args):
    vk_bot = bot.get_bot()

    user_id = message['user_id']
    chat_id = message.get('chat_id')
    user_name = vk_bot.get_user_name(user_id)
    msg_to_send = "Hello, %s!" % user_name

    if args.private or not chat_id:
        # Send message directly.
        vk_bot.send_to(msg_to_send, user_id=user_id)
    else:
        vk_bot.send_to(msg_to_send, chat_id=chat_id)
