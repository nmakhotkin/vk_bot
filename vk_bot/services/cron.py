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
import eventlet
import json
import time

from croniter import croniter

from vk_bot.bot import actions
from vk_bot.bot import bot
from vk_bot.bot import commands
from vk_bot import config
from vk_bot.db import api
from vk_bot.utils import log as logging
from vk_bot.utils import utils


CONF = config.CONF
LOG = logging.getLogger(__name__)

PERIODIC_CALLS = []


def periodic_call(pattern=None, threads=None, **kwargs):
    """Decorator for wrapping new periodic calls

    :param pattern: cron-pattern, type: string
    :param kwargs: arguments for function, dict.
    :return:
    """
    def decorator(func):
        PERIODIC_CALLS.append(
            {
                'name': func.__name__,
                'func_path': '.'.join([func.__module__, func.__name__]),
                'pattern': pattern,
                'arguments': kwargs,
                'threads': threads or 1
            }
        )
        return func
    return decorator


def initialize_periodic_calls():
    for pcall in PERIODIC_CALLS:
        name = pcall['name']
        pattern = pcall.get('pattern') or CONF.get('cron', name)

        pcall_db = api.get_periodic_call_by_name(name)

        start_time = datetime.datetime.now()
        next_time = croniter(pattern, start_time).get_next(datetime.datetime)

        target_method = pcall['func_path']
        arguments = pcall.get('arguments', {})

        values = {
            'execution_time': next_time,
            'pattern': pattern,
            'target_method': target_method,
            'arguments': json.dumps(arguments),
            'processing': False
        }

        if not pcall_db:
            values.update({'name': name})

            pcall_db = api.create_periodic_call(values)
        else:
            pcall_db = api.update_periodic_call(name, values)

        utils.add_semaphore(pcall_db.id, pcall.get('threads', 1))


def get_next_periodic_calls():
    return api.get_next_periodic_calls(datetime.datetime.now())


def end_processing(gt, pcall):
    next_time = utils.get_next_time(
        pcall.pattern,
        datetime.datetime.now()
    )

    next_time2 = utils.get_next_time(
        pcall.pattern, pcall.execution_time
    )

    if (pcall.remaining_executions is not None
            and pcall.remaining_executions == 0):
        api.delete_periodic_call(pcall.name)

        utils.SEMAPHORES[pcall.id].release()
        utils.remove_semaphore(pcall.id)
    else:
        api.update_periodic_call(
            pcall.name,
            {
                'execution_time': max(next_time, next_time2),
                'processing': False
            }
        )

        utils.SEMAPHORES[pcall.id].release()


def process_periodic_calls():
    """Long running thread processing next periodic calls

    :return:
    """
    while True:
        calls_to_process = get_next_periodic_calls()
        while not calls_to_process:
            calls = api.get_periodic_calls()

            now = datetime.datetime.now()
            nearest = min([c.execution_time for c in calls])

            time_to_sleep = (nearest - now).total_seconds()
            time_to_sleep = time_to_sleep if time_to_sleep > 0 else 1

            LOG.debug("Sleeping for %s s..." % time_to_sleep)

            time.sleep(time_to_sleep)
            calls_to_process = get_next_periodic_calls()

        for call in calls_to_process:
            func = utils.import_class(call.target_method)
            arguments = json.loads(call.arguments)

            values = {'processing': True}

            if call.remaining_executions and call.remaining_executions > 0:
                values['remaining_executions'] = call.remaining_executions - 1

            updated_call = api.update_periodic_call(
                call.name,
                values
            )

            if not utils.SEMAPHORES.get(call.id):
                utils.add_semaphore(call.id, 1)

            utils.SEMAPHORES[call.id].acquire()
            t = eventlet.spawn(func, **arguments)
            t.link(end_processing, updated_call)


@utils.log_execution("Sending dollar info...",
                     "Dollar info sent.",
                     "Sending dollar info failed")
@periodic_call(pattern=CONF.get('cron', 'send_dollar_info'))
def send_dollar_info():
    return actions.send_dollar_info()


@utils.log_execution("Sending euro info...",
                     "Euro info sent.",
                     "Sending euro info failed")
@periodic_call(pattern=CONF.get('cron', 'send_euro_info'))
def send_euro_info():
    return actions.send_euro_info()


@periodic_call(pattern=CONF.get('cron', 'process_commands'))
def process_commands():
    vk_bot = bot.get_bot()

    LOG.info("Reading messages...")

    messages = vk_bot.wait_for_messages()

    for msg in messages:
        if commands.is_command(msg['body']):
            try:
                LOG.info("Executing command '%s'..." % msg['body'])
                commands.execute_cmd(msg, msg['body'])
            except Exception as e:
                e_msg = "'%s' cmd failed: %s" % (msg['body'], e)
                LOG.warn(e_msg)
                vk_bot.answer_on_message(msg, e_msg)

    if messages:
        vk_bot.mark_messages_as_read(messages)
