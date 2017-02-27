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
import re

from bs4 import BeautifulSoup
import requests

from vk_bot.bot import bot
from vk_bot.utils import utils


DOLLAR_CHART_URL = (
    "http://j1.forexpf.ru/delta/prochart?type=USDRUB&amount=335"
    "&chart_height=340&chart_width=660&grtype=2&tictype=1&iId=5"
)
EURO_CHART_URL = (
    "http://j1.forexpf.ru/delta/prochart?type=EURRUB&amount=335&"
    "chart_height=340&chart_width=660&grtype=2&tictype=1&iId=5"
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
CAT_URL = "http://thecatapi.com/api/images/get?format=src&type=gif&size=med"
ANEKDOT_URL = "http://www.anekdot.ru/random/anekdot"
COLOR_PATTERN = re.compile(r"\[0m|\[38;5;[0-9]+;?[0-9]?m|\[1m|\x1b")


def answer_on_message(message, text):
    vk_bot = bot.get_bot()

    vk_bot.answer_on_message(message, text)


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


def send_euro_info(message=None):
    euro_info = utils.get_euro_info()

    text = (
        u"Курс евро на сегодня: %s.\n"
        u"Курс евро на завтра: %s"
        % (euro_info['today'], euro_info['tomorrow'])
    )

    if not message:
        bot.get_bot().send_to_main_picture(
            EURO_CHART_URL,
            text
        )
    else:
        bot.get_bot().answer_on_message(
            message,
            text,
            EURO_CHART_URL
        )


def send_weather(message, city):
    headers = {"Accept-Language": "ru"}
    r = requests.get('http://wttr.in/%s' % city, headers=headers)
    parser = BeautifulSoup(r.content, "html5lib", from_encoding="utf8")
    text = parser.find('body').text

    if text.find('┌') == -1:
        raise RuntimeError(text)

    forecast = text[:text.find('┌')]

    forecast_array = forecast.split('\n')

    # Remove first 15 characters starting 3rd line.
    replacement = []
    for item in forecast_array[2:]:
        item = disable_color(item)
        replacement += [item[15:]]

    replacement[1] = "Температура:\t%s" % replacement[1]
    replacement[2] = "Ветер:\t\t%s" % replacement[2]
    replacement[3] = "Видимость:\t%s" % replacement[3]
    replacement[4] = "Осадки:\t%s" % replacement[4]

    forecast_array[2:] = replacement

    forecast_array += ["Источник - wttr.in"]

    vk_bot = bot.get_bot()
    vk_bot.answer_on_message(message, '\n'.join(forecast_array))


def disable_color(s):
    return re.sub(COLOR_PATTERN, "", s)


def send_no(message):
    vk_bot = bot.get_bot()

    vk_bot.answer_on_message(message, "", photo_url=random.choice(NO_URLS))


def rulez(message):
    vk_bot = bot.get_bot()

    vk_bot.answer_on_message(message, "Absolutely agree!")


def cat(message):
    vk_bot = bot.get_bot()

    vk_bot.answer_on_message(message, "", doc_url=CAT_URL)


def anekdot(message):
    vk_bot = bot.get_bot()

    resp = requests.get(ANEKDOT_URL, headers={'User-Agent': 'HTTPie/0.9.2'})
    parsed = BeautifulSoup(resp.content, "html5lib")

    anekdots = parsed.findAll('div', {'class': 'text'})

    if not anekdots:
        vk_bot.answer_on_message(message, "Страница с анекдотами недоступна")
        return

    anekdot = "\n".join(list(anekdots[0].strings))

    vk_bot.answer_on_message(message, anekdot)
