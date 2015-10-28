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

import re


REMINDER_COMMAND = "bot напомни"
REMINDER_CMD_PATTERN = re.compile("^ *%s.*", re.IGNORECASE)


def validate_reminder_text(text):
    if REMINDER_CMD_PATTERN.match(text):
        raise RuntimeError("Нельзя создавать напоминалки для бота! Фиг Вам.")
