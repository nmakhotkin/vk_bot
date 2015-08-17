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
from vk_bot.utils import shell as sh_utils


CONF = config.CONF

# TODO(nmakhotkin): add more actions.


@crython.job(expr=CONF.get('cron', 'send_uptime'))
def send_uptime():
    uptime = sh_utils.execute_command('uptime')
    uptime_pp = uptime[:uptime.find('  ') - 1].strip()
    uptime_pp = "Kolyan's computer uptime:\n%s" % uptime_pp

    # Send uptime information to main chat.
    bot.get_bot().send_to_main(uptime_pp)


def setup():
    crython.tab.start()

    return crython.tab
