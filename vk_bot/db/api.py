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

import sqlalchemy as sa
from sqlalchemy import exc

from vk_bot.db import base
from vk_bot.db import models


def setup_db():
    try:
        models.PeriodicCall.metadata.create_all(base.get_engine())
    except sa.exc.OperationalError as e:
        raise RuntimeError("Failed to setup database: %s" % e)


@base.session_aware()
def create_periodic_call(values, session=None):
    call = models.PeriodicCall(**values)

    try:
        session.add(call)
    except exc.SQLAlchemyError as e:
        raise RuntimeError(
            "Duplicate entry for PeriodicCall: %s" % e
        )

    return call


def get_periodic_calls(**kwargs):
    query = base.model_query(models.PeriodicCall)
    return query.filter_by(**kwargs).all()


def get_periodic_call_by_id(id):
    query = base.model_query(models.PeriodicCall)

    return query.filter_by(id=id).first()


def get_periodic_call_by_name(name):
    query = base.model_query(models.PeriodicCall)

    return query.filter_by(name=name).first()


@base.session_aware()
def update_periodic_call(name, values, session=None):
    pcall = get_periodic_call_by_name(name)

    if not pcall:
        raise RuntimeError('Periodic call not found for name: %s' % id)

    pcall.update(values.copy())

    return pcall


@base.session_aware()
def delete_periodic_call(name, session=None):
    pcall = get_periodic_call_by_name(name)

    if not pcall:
        raise RuntimeError('Periodic call not found for name: %s' % id)

    session.delete(pcall)
