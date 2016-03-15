# coding=utf-8
# Copyright 2016 - Nikolay Makhotkin.
#
# Licensed under the Whatever You Want License.
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from vk_bot import config
from vk_bot.db import api as db_api


CONF = config.CONF


def _validate_alias(name, command, user):
    existing_aliases = db_api.get_aliases(user_id=user)

    aliases_limit = int(CONF.get('commands', 'aliases_per_user'))

    if len(existing_aliases) > aliases_limit:
        raise RuntimeError(
            "Нельзя создать больше %s алиасов, у Вас уже есть %s. "
            "Удалить можно с помощью команды 'стереть алиас <id>'. Посмотреть "
            "алиасы можно командой 'алиасы'."
            % (aliases_limit, len(existing_aliases))
        )


def create_alias(name, command, user):
    _validate_alias(name, command, user)

    alias = db_api.create_alias({
        'name': name,
        'command': command,
        'user_id': user
    })

    return alias


def get_aliases(user=None):
    if user:
        return db_api.get_aliases(user_id=user)
    else:
        return db_api.get_aliases()


def delete_alias(user, id):
    user_aliases = db_api.get_aliases(user_id=user)

    if not user_aliases:
        raise RuntimeError("У Вас еще нет алиасов.")

    alias_to_delete = db_api.get_alias_by_id(id)

    if alias_to_delete.id in [r.id for r in user_aliases]:
        db_api.delete_alias(id)
    else:
        raise RuntimeError("Неправильный id. Либо не Ваш алиас.")
