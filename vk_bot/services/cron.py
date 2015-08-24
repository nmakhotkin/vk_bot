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

import crython

from vk_bot import bot
from vk_bot import config
from vk_bot import utils
from vk_bot.utils import shell as sh_utils


CONF = config.CONF

DOLLAR_CHART_URL = (
    "http://j1.forexpf.ru/delta/prochart?type=USDRUB&amount=335"
    "&chart_height=340&chart_width=660&grtype=2&tictype=1&iId=5"
)


@crython.job(expr=CONF.get('cron', 'send_uptime'))
@utils.log_execution("Sending uptime...",
                     "Uptime is sent.",
                     "Sending uptime failed")
def send_uptime():
    uptime = sh_utils.execute_command('uptime')
    uptime_pp = uptime[:uptime.find('  ') - 1].strip()
    uptime_pp = "Kolyan's computer uptime:\n%s" % uptime_pp

    # Send uptime information to main chat.
    bot.get_bot().send_to_main(uptime_pp)


@crython.job(expr=CONF.get('cron', 'send_dollar_info'))
@utils.log_execution("Sending dollar info...",
                     "Dollar info sent.",
                     "Sending dollar info failed")
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


def setup():
    crython.tab.start()

    return crython.tab
