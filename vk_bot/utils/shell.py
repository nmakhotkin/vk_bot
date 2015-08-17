# Copyright 2015 - Nikolay Makhotkin.
#
# Licensed under the Whatever You Want License.
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import subprocess


def execute_command(cmd, stderr=False):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

    stdout, stderr = process.communicate()

    if stderr:
        return stdout, stderr
    else:
        return stdout
