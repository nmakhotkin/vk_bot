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
def get_next_periodic_calls(time, session=None):
    query = base.model_query(models.PeriodicCall)

    query = query.filter(models.PeriodicCall.execution_time < time)
    query = query.filter_by(processing=False)
    query = query.order_by(models.PeriodicCall.execution_time)

    return query.all()


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


@base.session_aware()
def create_alias(values, session=None):
    alias = models.Alias(**values)

    try:
        session.add(alias)
    except exc.SQLAlchemyError as e:
        raise RuntimeError(
            "Duplicate entry for Alias: %s" % e
        )

    return alias


def get_aliases(**kwargs):
    query = base.model_query(models.Alias)
    return query.filter_by(**kwargs).all()


def get_alias_by_id(id):
    query = base.model_query(models.Alias)

    return query.filter_by(id=id).first()


def get_alias_by_name(name):
    query = base.model_query(models.Alias)

    return query.filter_by(name=name).first()


@base.session_aware()
def update_alias(name, values, session=None):
    alias = get_alias_by_name(name)

    if not alias:
        raise RuntimeError('Alias not found for name: %s' % id)

    alias.update(values.copy())

    return alias


@base.session_aware()
def delete_alias(id, session=None):
    alias = get_alias_by_id(id)

    if not alias:
        raise RuntimeError('Alias not found for id: %s' % id)

    session.delete(alias)
