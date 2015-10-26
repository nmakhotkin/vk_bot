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

import shlex

from vk_bot.bot import actions
from vk_bot.bot import bot

DIRECT_COMMAND_TRIGGERS = [u"нет!", u"котик", u"анекдот"]
CONTAIN_COMMAND_TRIGGERS = [u"напомни"]


def is_command(string):
    string = string.lower()

    is_cmd = string.startswith('bot ') or string in DIRECT_COMMAND_TRIGGERS

    if is_cmd:
        return is_cmd

    for cmd in CONTAIN_COMMAND_TRIGGERS:
        if string.startswith(cmd):
            return True

    return False


class ArgumentParserError(Exception):
    pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def __init__(self,
                 prog=None,
                 vk_message=None,
                 **kwargs):
        super(ThrowingArgumentParser, self).__init__(
            prog,
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
    splitter = shlex.shlex(command, posix=True)
    splitter.whitespace_split = True

    arg_list = list(splitter)
    arg_list[0] = arg_list[0].lower()

    if arg_list[0] == 'bot':
        arg_list = arg_list[1:]
        arg_list[0] = arg_list[0].lower()

    parser = get_parser(message)

    args = parser.parse_args(arg_list)

    return args.func(message, args)


def get_parser(message):
    global_parser = ThrowingArgumentParser(
        'bot',
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

    parser = subparser.add_parser(
        'get-dollar-info',
        help="Shows current dollar information (picture and text)"
    )
    parser.set_defaults(func=send_dollar_info)

    parser = subparser.add_parser(
        'get-euro-info',
        help="\tShows current euro information (picture and text)"
    )
    parser.set_defaults(func=send_euro_info)

    parser = subparser.add_parser('нет!', help="Отвечает картинкой 'нет'")
    parser.set_defaults(func=send_no)

    parser = subparser.add_parser('rulez', help="Соглашается.")
    parser.set_defaults(func=rulez)

    parser = subparser.add_parser('котик', help="Загружает анимашку котика.")
    parser.set_defaults(func=cat)

    parser = subparser.add_parser(
        'анекдот',
        help="Печатает случайный анекдот."
    )
    parser.set_defaults(func=anekdot)

    parser = subparser.add_parser(
        'напомни',
        help="Добавляет напоминалку по заданному времени."
    )
    parser.add_argument(
        '-pattern',
        dest='pattern',
        help='Cron-паттерн',
        type=str,
        metavar='<* * * * * *>'
    )
    parser.add_argument(
        '-count',
        dest='count',
        type=int,
        default=1,
        help='Количество повторений',
        metavar='<integer>'
    )
    parser.add_argument(
        'text',
        type=str,
        help='Текст напоминания',
        metavar='<text>'
    )
    parser.set_defaults(func=add_reminder)

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


def send_dollar_info(message, args):
    actions.send_dollar_info(message)


def send_euro_info(message, args):
    actions.send_euro_info(message)


def send_no(message, args):
    actions.send_no(message)


def rulez(message, args):
    actions.rulez(message)


def cat(message, args):
    actions.cat(message)


def anekdot(message, args):
    actions.anekdot(message)


def add_reminder(message, args):
    raise NotImplementedError("Not Implemented.")

    # print(args.pattern)
    # print(args.count)
    # print(args.text)
