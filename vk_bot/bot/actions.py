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

import random

from vk_bot.bot import bot
from vk_bot.utils import shell as sh_utils
from vk_bot.utils import utils


DOLLAR_CHART_URL = (
    "http://j1.forexpf.ru/delta/prochart?type=USDRUB&amount=335"
    "&chart_height=340&chart_width=660&grtype=2&tictype=1&iId=5"
)

NO_URLS = [
    "http://vignette2.wikia.nocookie.net/dont-starve/images/5/58/%D0"
    "%9D%D0%95%D0%A2!.jpg/revision/latest?cb=20130716113721&path-prefix=ru",
    "http://ratingmax.ru/wp-content/uploads/2015/06/net.jpg",
    "http://img.dni.ru/binaries/v3_main/285381.jpg",
    "https://ucare.timepad.ru/ef4ca052-f7db-4860-b59b-41bd3af47fe1/",
    "http://www.2do2go.ru/uploads/"
    "a26d318ca40dee9989be11dc4a0ba979_w256_h256.jpg"
]


def send_dollar_info(message=None):
    dollar_info = utils.get_dollar_info()

    text = (
        u"Курс доллара на сегодня: %s.\n"
        u"Курс доллара на завтра: %s"
        % (dollar_info['today'], dollar_info['tomorrow'])
    )

    if not message:
        bot.get_bot().send_to_main_picture(
            DOLLAR_CHART_URL,
            text
        )
    else:
        bot.get_bot().answer_on_message(
            message,
            text,
            DOLLAR_CHART_URL
        )


def send_uptime():
    uptime = sh_utils.execute_command('uptime')
    uptime_pp = uptime[:uptime.find('  ') - 1].strip()
    uptime_pp = "Kolyan's computer uptime:\n%s" % uptime_pp

    # Send uptime information to main chat.
    bot.get_bot().send_to_main(uptime_pp)


def send_no(message):
    vk_bot = bot.get_bot()

    vk_bot.answer_on_message(message, "", photo_url=random.choice(NO_URLS))


def rulez(message):
    vk_bot = bot.get_bot()

    vk_bot.answer_on_message(message, "Absolutely agree!")
