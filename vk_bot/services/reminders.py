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

import json
import re

from vk_bot import config
from vk_bot.db import api as db_api
from vk_bot.utils import utils


CONF = config.CONF
REMINDER_COMMAND = "напомни"
REMINDER_CMD_PATTERN = re.compile(
    "^ *(bot {0}|{0}).*".format(REMINDER_COMMAND),
    re.IGNORECASE
)


def validate_reminder_text(text):
    if REMINDER_CMD_PATTERN.match(text):
        raise RuntimeError("Нельзя создавать напоминалки для бота! Фиг Вам.")


def validate_reminder(count, user, text):
    max_count = int(CONF.get('commands', 'reminders_count'))

    if count > max_count or count < 1:
        raise RuntimeError(
            "Ограничение на количество повторений: 0-%s; текущее: %s"
            % (max_count, count)
        )

    validate_reminder_text(text)
    existing_reminders = db_api.get_periodic_calls(user_id=user)

    max_reminders = int(CONF.get('commands', 'reminders_per_user'))
    if len(existing_reminders) >= max_reminders:
        raise RuntimeError(
            "Нельзя создать больше %s напоминалок, у Вас уже есть %s. "
            "Удалить можно с помощью команды 'забудь <id>'. Посмотреть "
            "напоминалки можно командой 'мои напоминалки'."
            % (max_reminders, len(existing_reminders))
        )


def get_reminders(user):
    return db_api.get_periodic_calls(user_id=user)


def add_reminder(message, name, count, user, pattern, text):
    validate_reminder(count, user, text)

    next_time = utils.get_next_time(pattern)

    pcall = db_api.create_periodic_call(
        {
            'name': name,
            'arguments': json.dumps({
                'message': message,
                'text': text
            }),
            'target_method': 'vk_bot.bot.actions.answer_on_message',
            'pattern': pattern,
            'remaining_executions': count,
            'execution_time': next_time,
            'user_id': user
        }
    )

    utils.add_semaphore(pcall.id, 1)

    return pcall


def delete_reminder(name, user):
    user_reminders = db_api.get_periodic_calls(user_id=user)

    if not user_reminders:
        raise RuntimeError("У Вас еще нет напоминалок.")

    reminder_to_delete = db_api.get_periodic_call_by_name(name)

    if reminder_to_delete.id in [r.id for r in user_reminders]:
        db_api.delete_periodic_call(name)
    else:
        raise RuntimeError("Неправильный id.")
