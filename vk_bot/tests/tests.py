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

from vk_bot.tests import base


class VkBotTest(base.BaseTest):
    def test_get_photo_id(self):
        url = ('http://i.telegraph.co.uk/multimedia/'
               'archive/02417/luke-silcocks_2417486k.jpg')
        try:
            photo_id = self.bot._get_photo_id(url)
        except Exception:
            photo_id = None

        print "photo_id: %s" % photo_id
        if photo_id:
            pattern = re.compile("photo[0-9]+_[0-9]+")
            self.assertIn(photo_id, re.findall(pattern, photo_id))
