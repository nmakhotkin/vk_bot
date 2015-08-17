# Copyright 2015 - Nikolay Makhotkin.
#
# Licensed under the Whatever You Want License.
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from oslo_config import cfg
from oslo_service import periodic_task
from oslo_service import threadgroup

from vk_bot import bot
from vk_bot import config
from vk_bot.utils import shell as sh_utils


CONF = config.CONF
OSLO_CONF = cfg.CONF


class VkBotPeriodicTasks(periodic_task.PeriodicTasks):
    def __init__(self, conf):
        super(VkBotPeriodicTasks, self).__init__(conf)

        # TODO(nmakhotkin): uncomment this when vk bot becomes more reliable.
        # self.add_task_with_spacing(
        #    task=send_uptime,
        #    spacing=int(CONF.get('periodic', 'send_uptime_interval')),
        # )

    def add_task_with_spacing(self, task, spacing):
        vk_task = periodic_task.periodic_task(
            spacing=spacing,
            run_immediately=True
        )

        self.add_periodic_task(vk_task(task))


def send_uptime(self, ctx):
    uptime = sh_utils.execute_command('uptime')
    uptime_pp = uptime[:uptime.find('  ') - 1].strip()
    uptime_pp = "Kolyan's computer uptime:\n%s" % uptime_pp

    bot.get_bot().send_to_main(uptime_pp)


def setup():
    tg = threadgroup.ThreadGroup()
    pt = VkBotPeriodicTasks(OSLO_CONF)

    tg.add_dynamic_timer(
        pt.run_periodic_tasks,
        initial_delay=None,
        periodic_interval_max=5,
        context=None
    )

    return tg
