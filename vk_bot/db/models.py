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

from sqlalchemy import types as st

from vk_bot.db import base


class PeriodicCall(base.ModelBase):
    __tablename__ = 'triggers'

    id = sa.Column(
        st.Integer,
        sa.Sequence('periodic_call_id_seq'),
        primary_key=True
    )
    name = sa.Column(st.String(80), unique=True)
    user_id = sa.Column(st.String(20), nullable=True)

    target_method = sa.Column(st.String(length=200))
    arguments = sa.Column(st.Text())
    execution_time = sa.Column(sa.DateTime, nullable=False)
    pattern = sa.Column(
        sa.String(100),
        nullable=True,
        default='0 0 0 30 2 0'  # Set default to 'never'.
    )
    remaining_executions = sa.Column(sa.Integer)
    processing = sa.Column(sa.Boolean, default=False)
