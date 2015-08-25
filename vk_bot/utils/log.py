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
from logging import config as l_c

from vk_bot import config
from vk_bot.utils import file_utils


CONF = config.CONF
LOG_FORMAT = '%(asctime)s %(module)-25s %(levelname)-8s: %(message)s'


def configure():
    l_c.fileConfig(
        file_utils.get_file_path('../logging.conf'),
        disable_existing_loggers=False
    )


def getLogger(name):
    return logging.getLogger(name)
