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
import sys

from vk_bot.bot import bot
from vk_bot import version


class ArgumentParserError(Exception):
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def __init__(self,
                 prog=None,
                 version=None,
                 vk_message=None,
                 **kwargs):
        super(ThrowingArgumentParser, self).__init__(
            prog,
            version=version,
            **kwargs
        )

        self.vk_message = vk_message

    def error(self, message):
        raise ArgumentParserError(message)

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)
            bot.get_bot().answer_on_message(self.vk_message, message)


def execute_cmd(message, command):
    command = command.split(' ')
    command = command[1:]
    parser = get_parser(message)

    args = parser.parse_args(command)

    return args.func(message, args)


def get_parser(message):
    global_parser = ThrowingArgumentParser(
        'bot',
        version=version.version_string(),
        vk_message=message,
        add_help=False
    )

    subparser = global_parser.add_subparsers(dest='action')

    parser = subparser.add_parser('hello', help="Says hello to the user.")
    parser.add_argument(
        '-private',
        action='store_true',
        dest='private',
    )
    parser.set_defaults(func=hello)

    parser = subparser.add_parser('help', help="Shows help.")
    parser.set_defaults(func=show_help)

    return global_parser


def show_help(message, args):
    parser = get_parser(message)
    vk_bot = bot.get_bot()

    help = parser.format_help()
    vk_bot.answer_on_message(message, help)


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
