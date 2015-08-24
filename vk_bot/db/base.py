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

import six

import sqlalchemy as sa
from sqlalchemy.ext import declarative
from sqlalchemy import orm

from vk_bot import config
from vk_bot import utils


CONF = config.CONF
_DB_SESSION_THREAD_LOCAL_NAME = "db_sql_alchemy_session"
_ENGINE = None


class _ModelBase(object):
    """Base class for all Mistral SQLAlchemy DB Models."""

    __table__ = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self, values):
        """Make the model object behave like a dict."""
        for k, v in six.iteritems(values):
            setattr(self, k, v)

    def to_dict(self):
        """sqlalchemy based automatic to_dict method."""
        d = {}

        for col in self.__table__.columns:
            if col.name and hasattr(self, col.name):
                d[col.name] = getattr(self, col.name)

        return d

    def __repr__(self):
        return '%s %s' % (type(self).__name__, self.to_dict().__repr__())


ModelBase = declarative.declarative_base(cls=_ModelBase)


def get_engine():
    global _ENGINE

    if not _ENGINE:
        _ENGINE = sa.create_engine(
            CONF.get('database', 'connection')
        )

    return _ENGINE


def _get_session():
    session_maker = orm.sessionmaker(
        bind=get_engine(),
        expire_on_commit=False
    )

    return orm.scoped_session(session_maker)


def _get_thread_local_session():
    return utils.get_thread_local(_DB_SESSION_THREAD_LOCAL_NAME)


def _get_or_create_thread_local_session():
    ses = _get_thread_local_session()

    if ses:
        return ses, False

    ses = _get_session()
    _set_thread_local_session(ses)

    return ses, True


def _set_thread_local_session(session):
    utils.set_thread_local(_DB_SESSION_THREAD_LOCAL_NAME, session)


def session_aware(param_name="session"):
    """Decorator for methods working within db session."""

    def _decorator(func):
        def _within_session(*args, **kw):
            # If 'created' flag is True it means that the transaction is
            # demarcated explicitly outside this module.
            ses, created = _get_or_create_thread_local_session()

            try:
                kw[param_name] = ses

                result = func(*args, **kw)

                if created:
                    ses.commit()

                return result
            except Exception:
                if created:
                    ses.rollback()
                raise
            finally:
                if created:
                    _set_thread_local_session(None)
                    ses.close()

        _within_session.__doc__ = func.__doc__

        return _within_session

    return _decorator


@session_aware()
def model_query(model, session=None):
    """Query helper.

    :param model: base model to query
    """
    return session.query(model)
