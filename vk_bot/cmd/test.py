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

import logging

from vk_bot import config
config.parse()

from vk_bot.bot import bot


logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger(__name__)


def main():
    vk_bot = bot.get_bot()

    LOG.info("Start test...")

    vk_bot.test()


if __name__ == '__main__':
    main()
