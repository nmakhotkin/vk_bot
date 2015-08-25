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
import json
import time
import threading

from croniter import croniter

from vk_bot import bot
from vk_bot import config
from vk_bot.db import api
from vk_bot.utils import log as logging
from vk_bot.utils import shell as sh_utils
from vk_bot.utils import utils


CONF = config.CONF
LOG = logging.getLogger(__name__)

DOLLAR_CHART_URL = (
    "http://j1.forexpf.ru/delta/prochart?type=USDRUB&amount=335"
    "&chart_height=340&chart_width=660&grtype=2&tictype=1&iId=5"
)
PERIODIC_CALLS = []


def periodic_call(pattern=None, **kwargs):
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
                'arguments': kwargs
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
            'arguments': json.dumps(arguments)
        }

        if not pcall_db:
            values.update({'name': name})

            api.create_periodic_call(values)
        else:
            api.update_periodic_call(name, values)


def get_next_periodic_calls():
    return api.get_next_periodic_calls(datetime.datetime.now())


def get_next_time(pattern, start_time):
    return croniter(pattern, start_time).get_next(datetime.datetime)


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

            LOG.info("Sleeping %s..." % time_to_sleep)

            time.sleep(time_to_sleep if time_to_sleep > 0 else 0)
            calls_to_process = get_next_periodic_calls()

        for call in calls_to_process:
            func = utils.import_class(call.target_method)
            arguments = json.loads(call.arguments)

            api.update_periodic_call(
                call.name,
                {
                    'execution_time': get_next_time(
                        call.pattern, call.execution_time
                    )
                }
            )
            t = threading.Thread(target=func, kwargs=arguments)

            t.start()


@utils.log_execution("Sending uptime...",
                     "Uptime is sent.",
                     "Sending uptime failed")
@periodic_call(pattern=CONF.get('cron', 'send_uptime'))
def send_uptime():
    uptime = sh_utils.execute_command('uptime')
    uptime_pp = uptime[:uptime.find('  ') - 1].strip()
    uptime_pp = "Kolyan's computer uptime:\n%s" % uptime_pp

    # Send uptime information to main chat.
    bot.get_bot().send_to_main(uptime_pp)


@utils.log_execution("Sending dollar info...",
                     "Dollar info sent.",
                     "Sending dollar info failed")
@periodic_call(pattern=CONF.get('cron', 'send_dollar_info'))
def send_dollar_info():
    dollar_info = utils.get_dollar_info()

    text = (
        u"Курс доллара на сегодня: %s.\n"
        u"Курс доллара на завтра: %s"
        % (dollar_info['today'], dollar_info['tomorrow'])
    )

    bot.get_bot().send_to_main_picture(
        DOLLAR_CHART_URL,
        text
    )
