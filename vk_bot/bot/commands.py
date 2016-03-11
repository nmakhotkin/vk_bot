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
import copy
import json
import sys

import shlex

from vk_bot.bot import actions
from vk_bot.bot import bot
from vk_bot import config
from vk_bot.services import aliases as alias_service
from vk_bot.services import reminders


DIRECT_COMMAND_TRIGGERS = [
    u"нет!",
    u"котик",
    u"анекдот",
    u"напоминалки",
    u"алиас",
    u"алиасы",
]
CONTAIN_COMMAND_TRIGGERS = [
    u"напомни ",
    u"забудь ",
    u"погода",
    u"забудь-алиас "
]
CONF = config.CONF


def is_command(string):
    string = string.lower()

    if string in DIRECT_COMMAND_TRIGGERS:
        return True

    for cmd in CONTAIN_COMMAND_TRIGGERS:
        if string.startswith(cmd):
            return True

    try:
        parse_command(string)
    except Exception:
        pass
    else:
        return True

    return False


def get_cmd_if_alias(message):
    aliases = alias_service.get_aliases(message['user_id'])

    if not aliases:
        return None

    for alias in aliases:
        if message['body'] == alias.name:
            return alias.command


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


def parse_command(string, message=None):
    splitter = shlex.shlex(string, posix=True)
    splitter.whitespace_split = True

    arg_list = list(splitter)
    arg_list[0] = arg_list[0].lower()

    if arg_list[0] == 'bot':
        arg_list = arg_list[1:]
        arg_list[0] = arg_list[0].lower()

    parser = get_parser(message)

    return parser.parse_args(arg_list)


def execute_cmd(message, command):
    args = parse_command(message=message, string=command)

    return args.func(message, args)


def get_parser(message=None):
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

    parser = subparser.add_parser('help', help="Показывает справку.")
    parser.add_argument(
        'command',
        metavar='<command>',
        help='Показывает справку по команде.',
        nargs='?'
    )
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
        'pattern',
        help='Cron-паттерн',
        type=str,
        metavar='<* * * * *>'
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
        '-broadcast',
        action='store_true',
        help='Флаг, показывающий, отправлять ли напоминалку в главный чат',
    )
    parser.add_argument(
        '-user-id',
        type=str,
        help='Идентификатор пользователя',
        metavar='<1234567>'
    )
    parser.add_argument(
        'text',
        type=str,
        help='Текст напоминания',
        metavar='<text>'
    )
    parser.set_defaults(func=add_reminder)

    parser = subparser.add_parser(
        'напоминалки',
        help="Показывает собственные напоминалки."
    )
    parser.set_defaults(func=get_reminders)

    parser = subparser.add_parser(
        'забудь',
        help="Удаляет собственную напоминалку."
    )
    parser.add_argument(
        'id',
        type=str,
        help='Идентификатор напоминалки',
        metavar='<id>'
    )
    parser.set_defaults(func=remove_reminder)

    parser = subparser.add_parser(
        'погода',
        help="Показывает текущую погоду."
    )
    parser.add_argument(
        'city',
        type=str,
        nargs='?',
        help='Город для прогноза',
        default='saratov'
    )
    parser.set_defaults(func=send_weather)

    parser = subparser.add_parser(
        'алиас',
        help="Создаёт алиас для команды."
    )
    parser.add_argument(
        'name',
        type=str,
        help='Имя алиаса (то, что будет использоваться в качестве команды).',
    )
    parser.add_argument(
        'command',
        type=str,
        help='Команда для алиаса.',
    )
    parser.set_defaults(func=create_alias)

    parser = subparser.add_parser(
        'забудь-алиас',
        help="Удаляет алиас."
    )
    parser.add_argument(
        'id',
        type=str,
        help='id алиаса.',
    )
    parser.set_defaults(func=remove_alias)

    parser = subparser.add_parser(
        'алиасы',
        help="Показывает алиасы."
    )
    parser.set_defaults(func=get_aliases)

    return global_parser


def show_help(message, args):
    parser = get_parser(message)
    vk_bot = bot.get_bot()

    if not args.command:
        help_str = parser.format_help()
        vk_bot.answer_on_message(message, help_str)

        return

    commands = parser._subparsers._actions[0]

    if args.command not in commands.choices:
        raise RuntimeError("Command does not exist: %s" % args.command)

    help_str = commands.choices[args.command].format_help()
    vk_bot.answer_on_message(message, help_str)


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


def send_weather(message, args):
    actions.send_weather(message, args.city)


def rulez(message, args):
    actions.rulez(message)


def cat(message, args):
    actions.cat(message)


def anekdot(message, args):
    actions.anekdot(message)


def get_reminders(message, args):
    user_reminders = reminders.get_reminders(message['user_id'])

    vk_bot = bot.get_bot()

    if not user_reminders:
        vk_bot.answer_on_message(message, "Ещё нет напоминалок.")
        return

    output = []
    for index, r in enumerate(user_reminders):
        arguments = json.loads(r.arguments)
        output.append(
            "%s. %s, '%s', След.выполнение: %s"
            % (
                index + 1,
                r.name,
                arguments['text'],
                r.execution_time.strftime("%H:%M:%S, %d.%m.%Y")
            )
        )

    vk_bot.answer_on_message(message, '\n'.join(output))


def add_reminder(message, args):
    name = message['id']
    user_id = message['user_id']

    vk_bot = bot.get_bot()

    msg_to_db = copy.deepcopy(message)

    if args.broadcast and args.user_id:
        raise RuntimeError(
            "Невозможно одновременно использовать -broadcast и -user-id"
        )

    if args.broadcast:
        msg_to_db['chat_id'] = vk_bot.main_chat['id']

    if args.user_id:
        msg_to_db['user_id'] = args.user_id

    reminder = reminders.add_reminder(
        msg_to_db,
        name,
        args.count,
        user_id,
        args.pattern,
        args.text
    )

    vk_bot.answer_on_message(
        message,
        "Напоминалка создана; id = %s." % reminder.name
    )


def remove_reminder(message, args):
    name = args.id
    user = message['user_id']

    reminders.delete_reminder(name, user)

    vk_bot = bot.get_bot()
    vk_bot.answer_on_message(message, "Напоминалка удалена.")


def create_alias(message, args):
    name = args.name
    command = args.command
    user = message['user_id']

    if not is_command(command):
        raise RuntimeError("Некорректная команда для алиаса: %s" % command)

    if is_command(name):
        raise RuntimeError(
            "Имя алиаса пересекается с существующей командой: %s" % name
        )

    vk_bot = bot.get_bot()

    alias = alias_service.create_alias(name, command, user)

    vk_bot.answer_on_message(message, 'Алиас создан. id = %s.' % alias.id)


def get_aliases(message, args):
    user_aliases = alias_service.get_aliases(message['user_id'])

    vk_bot = bot.get_bot()

    if not user_aliases:
        vk_bot.answer_on_message(message, "Ещё нет алиасов.")
        return

    output = []
    for i, a in enumerate(user_aliases):
        output.append(
            "%s. %s, команда = '%s'" % (
                i + 1,
                a.name,
                a.command
            )
        )

    vk_bot.answer_on_message(message, '\n'.join(output))


def remove_alias(message, args):
    user = message['user_id']
    id = args.id

    alias_service.delete_alias(user, id)

    vk_bot = bot.get_bot()
    vk_bot.answer_on_message(message, "Алиас удален.")
