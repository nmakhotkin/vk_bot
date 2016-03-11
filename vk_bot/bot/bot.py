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

import time
import requests
import vk

from vk_bot import config
from vk_bot.utils import log as logging
from vk_bot.utils import utils


CONF = config.CONF
MAIN_CHAT_ID = CONF.get('chat', 'main')
BOT = None
NEW_MESSAGE_EVENT = 4
LOG = logging.getLogger(__name__)


def get_bot():
    global BOT

    if not BOT:
        app_id = CONF.get('auth', 'app_id')
        scope = 'messages,friends,photos,docs'
        email = CONF.get('auth', 'email')
        password = CONF.get('auth', 'password')

        BOT = VkBot(email, password, app_id, scope)

    return BOT


class VkBot(object):
    def __init__(self, email, password, app_id, scope):
        self.app_id = app_id

        self._api = vk.OAuthAPI(
            app_id=app_id,
            user_login=email,
            user_password=password,
            scope=scope
        )
        self.ts = None
        self._main_chat = None
        self.msg_longpoll_server_info = None

    @property
    def api(self):
        if not self._api.access_token:
            self._api.get_access_token()
        return self._api

    @property
    def main_chat(self):
        if not self._main_chat:
            chat = self.api.messages.getChat(chat_id=MAIN_CHAT_ID)

            if not chat:
                raise Exception(
                    "The chat not found for chat id: %s" % MAIN_CHAT_ID
                )

            self._main_chat = chat

        return self._main_chat

    def get_unread_messages(self):
        read_found = False
        unread = []
        offset = 0
        batch_size = 50

        while not read_found:
            messages = self._get_messages(offset, batch_size)

            messages = messages['items']

            for index, msg in enumerate(messages):
                if msg['read_state'] == 1:
                    read_found = True
                    messages = messages[:index]

                    break

            offset += batch_size
            unread += messages

        return unread

    def mark_messages_as_read(self, messages):
        message_ids = [str(m['id']) for m in messages]

        string_ids = ','.join(message_ids)

        return self.api.messages.markAsRead(
            message_ids=string_ids
        )

    def _get_messages(self, offset=0, count=1, last_id=None):
        params = {
            'offset': offset,
            'count': count
        }

        if last_id:
            params['last_message_id'] = last_id

        return self.api.messages.get(**params)

    def send_to_main(self, message):
        return self.api.messages.send(
            chat_id=self.main_chat['id'],
            message=message
        )

    def answer_on_message(self, message, answer,
                          photo_url=None, doc_url=None):
        user_id = message['user_id']
        chat_id = message.get('chat_id')

        user_id = user_id if not chat_id else None

        self.send_to(
            answer,
            user_id=user_id,
            chat_id=chat_id,
            photo_url=photo_url,
            doc_url=doc_url
        )

    def _upload_photos_by_urls_in_message(self, message):
        """Adds photos in message by their URLs.

        Uploads photos by given URLs in message, cut these URLs out message
        and get dict containing media ids.

        :param message:
        :return: Dict structure for vk API messages.send.
        """
        urls = utils.get_urls(message)

        if not urls:
            return {'message': message}

        ids = []

        for url in urls:
            photo_id = None

            try:
                photo_id = self._get_media_id(url, 'photo')
            except Exception:
                pass
            else:
                message = message.replace(url, '', 1)
            finally:
                if photo_id:
                    ids.append(photo_id)

        return {
            'message': message,
            'attachment': ','.join(ids)
        }

    def send_to(self, message, user_id=None, chat_id=None,
                photo_url=None, doc_url=None):
        if not (bool(user_id) ^ bool(chat_id)):
            raise RuntimeError(
                "Only one of [user_id, chat_id] should be specified."
            )

        if photo_url and doc_url:
            raise RuntimeError(
                "Only at most one of [photo_url, doc_url] could be specified."
            )

        params = self._upload_photos_by_urls_in_message(message)

        if user_id:
            params['user_id'] = user_id
        elif chat_id:
            params['chat_id'] = chat_id

        if photo_url or doc_url:
            try:
                media_url = photo_url or doc_url
                media_type = 'photo' if photo_url else 'file'
                media_id = self._get_media_id(media_url, media_type)
            except Exception as e:
                LOG.exception(e)
                media_id = None

            if media_id:
                if params.get('attachment'):
                    params['attachment'] = ','.join(
                        [params['attachment'], media_id]
                    )
                else:
                    params['attachment'] = media_id
            else:
                message += u"\nПрикрепление не загрузилось."

        return self.api.messages.send(**params)

    def send_to_main_picture(self, picture_url, message=None):
        try:
            photo_id = self._get_media_id(picture_url)
        except Exception as e:
            LOG.exception(e)
            photo_id = None

        params = {
            'chat_id': self.main_chat['id']
        }

        if photo_id:
            params['attachment'] = photo_id
        else:
            message += u"\nКартинка не загрузилась."

        if message:
            params.update({'message': message})

        return self.api.messages.send(**params)

    def get_user_name(self, user_id):
        user = self.api.users.get(
            user_ids=user_id
        )

        if not user:
            return

        return user[0]['first_name']

    @utils.with_retry()
    def _get_photo_server_url(self):
        server_url = self.api.photos.getMessagesUploadServer()
        return server_url.get('upload_url')

    @utils.with_retry()
    def _get_docs_server_url(self):
        server_url = self.api.docs.getUploadServer()
        return server_url.get('upload_url')

    @utils.with_retry()
    def _get_messages_longpoll_server(self, timeout=20):
        server_info = self.api.messages.getLongPollServer()

        server_info['wait'] = timeout

        self.msg_longpoll_server_info = server_info.copy()

        return self._construct_msg_long_poll_url(**server_info)

    @staticmethod
    def _construct_msg_long_poll_url(server, key, ts, wait=20):
        info = {
            'server': server,
            'key': key,
            'ts': ts,
            'wait': wait
        }

        return ("http://%(server)s?act=a_check&"
                "key=%(key)s&ts=%(ts)s&wait=%(wait)s&mode=2" % info)

    @utils.with_retry()
    def _wait_for_event(self, timeout=20, ts=None):
        if not self.msg_longpoll_server_info:
            url = self._get_messages_longpoll_server(timeout)
        else:
            url = self._construct_msg_long_poll_url(
                self.msg_longpoll_server_info['server'],
                self.msg_longpoll_server_info['key'],
                ts,
                timeout
            )

        resp = requests.get(url)

        try:
            resp = resp.json()
        except (TypeError, ValueError):
            resp = {'error': resp.content}

        return resp

    def _handle_longpoll_fail(self, resp):
        error = resp.get('failed')

        if error in [2, 3]:
            self._get_messages_longpoll_server()

    def wait_for_messages(self):
        ts = self.ts
        is_msg = False
        msg_ids = []

        while not is_msg:
            LOG.debug("Waiting for event...")

            resp = self._wait_for_event(ts=ts)

            if 'ts' in resp:
                ts = resp['ts']

            if 'failed' in resp:
                LOG.warn("LongPoll connection failed: %s" % resp)

                self._handle_longpoll_fail(resp)
                continue

            if 'error' in resp:
                LOG.warning(
                    "Error while waiting for event: %s" % resp['error']
                )
                # Pause requesting on 1 sec.
                time.sleep(1)
                continue

            updates = resp['updates']

            if updates:
                LOG.info("Event: %s" % resp)
            else:
                LOG.debug("Event: %s" % resp)

            for update in updates:
                if update[0] == NEW_MESSAGE_EVENT:
                    is_msg = True
                    msg_ids += [str(update[1])]

        self.ts = ts
        string_ids = ','.join(msg_ids)

        messages = self.api.messages.getById(message_ids=string_ids)
        return messages['items']

    @utils.with_retry()
    def _get_media_id(self, media_url, media_type='photo'):
        if media_type not in ['photo', 'file']:
            raise RuntimeError("Unsupported media type: %s" % media_type)

        server_url = None
        if media_type == 'photo':
            server_url = self._get_photo_server_url()
        elif media_type == 'file':
            server_url = self._get_docs_server_url()

        LOG.info("Server upload URL: %s" % server_url)

        resp = utils.upload_file_on_server(
            server_url,
            media_url,
            entity_type=media_type
        )

        params = {
            media_type: [resp[media_type]]
        }

        if media_type == 'photo':
            params.update({
                'server': resp['server'],
                'hash': [resp['hash']]
            })

        media_info = {}
        if media_type == 'photo':
            media_info = self.api.photos.saveMessagesPhoto(**params)
        elif media_type == 'file':
            media_info = self.api.docs.save(**params)

            # That kind of hack.
            media_type = 'doc'

        return (
            "%s%s_%s" % (
                media_type,
                media_info[0]['owner_id'],
                media_info[0]['id']
            )
        )

    def test(self):
        LOG.info("Sending test info...")

        self.send_to_main(
            'VkBot Test. This is automatically constructed message.'
        )

        LOG.info("Sent.")
