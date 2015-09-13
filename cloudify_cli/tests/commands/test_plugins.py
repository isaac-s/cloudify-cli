########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

"""
Tests all commands that start with 'cfy plugins'
"""

from mock import MagicMock
from cloudify_cli.tests import cli_runner
from cloudify_cli.tests.commands.test_cli_command import CliCommandTest
from cloudify_cli.tests.commands.test_cli_command import PLUGINS_DIR


class PluginsTest(CliCommandTest):

    def setUp(self):
        super(PluginsTest, self).setUp()
        self._create_cosmo_wd_settings()

    def test_plugins_list(self):
        self.client.plugins.list = MagicMock(return_value=[])
        cli_runner.run_cli('cfy plugins list')

    def test_plugins_delete(self):
        self.client.plugins.delete = MagicMock()
        cli_runner.run_cli('cfy plugins delete -id a-plugin-id')

    def test_plugins_upload(self):
        self.client.plugins.upload = MagicMock()
        cli_runner.run_cli('cfy plugins upload -p '
                           '{0}/plugin.tar.gz '
                           '-id my_plugin_id'.format(PLUGINS_DIR))

    def test_plugins_download(self):
        self.client.plugins.download = MagicMock(return_value='some_file')
        cli_runner.run_cli('cfy plugins download -id a-plugin-id')
