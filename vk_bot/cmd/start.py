# Copyright 2015 - Nikolay Makhotkin.
#
# Licensed under the Whatever You Want License.
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import eventlet

eventlet.monkey_patch(
    os=True,
    select=True,
    socket=True,
    thread=True,
    time=True
)

from vk_bot import config
config.parse()

from vk_bot.db import api
from vk_bot.services import cron


def main():
    api.setup_db()
    cron_thread = cron.setup()
    thread = eventlet.spawn(cron_thread.join)

    print('Vk bot started.')

    thread.wait()


if __name__ == '__main__':
    main()
