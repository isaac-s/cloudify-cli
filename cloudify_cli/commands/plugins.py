########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

"""
Handles all commands that start with 'cfy plugins'
"""

from cloudify_cli import utils
from cloudify_cli.logger import get_logger
from cloudify_cli.utils import print_table
from cloudify_cli.exceptions import CloudifyCliError

# todo(adaml): merge with blueprints
SUPPORTED_ARCHIVE_TYPES = ['zip', 'tar', 'tar.gz', 'tar.bz2']


def delete(plugin_id):
    logger = get_logger()
    management_ip = utils.get_management_server_ip()
    logger.info("Deleting plugin '{0}' from management server {1}"
                .format(plugin_id, management_ip))
    client = utils.get_rest_client(management_ip)
    client.plugins.delete(plugin_id)
    logger.info('Deleted plugin successfully')


def upload(plugin_path, plugin_id):
    logger = get_logger()
    management_ip = utils.get_management_server_ip()
    for archive_type in SUPPORTED_ARCHIVE_TYPES:
        if plugin_path.name.endswith('.{0}'.format(archive_type)):
            break
    else:
        raise CloudifyCliError(
            "Can't publish archive {0} - it's of an unsupported archive type. "
            "Supported archive types: {1}".format(plugin_path.name,
                                                  SUPPORTED_ARCHIVE_TYPES))
    logger.info("Uploading plugin '{0}' at management server {1}"
                .format(plugin_path.name, management_ip))
    client = utils.get_rest_client(management_ip)
    plugin = client.plugins.upload(plugin_path.name, plugin_id)
    logger.info("Uploaded plugin, plugin's id is: {0}"
                .format(plugin.id))


def download(plugin_id, output):
    logger = get_logger()
    management_ip = utils.get_management_server_ip()
    logger.info("Downloading plugin '{0}' ...".format(plugin_id))
    client = utils.get_rest_client(management_ip)
    target_file = client.plugins.download(plugin_id, output)
    logger.info("plugin '{0}' has been downloaded successfully as '{1}'"
                .format(plugin_id, target_file))


def ls():
    logger = get_logger()
    management_ip = utils.get_management_server_ip()
    client = utils.get_rest_client(management_ip)
    logger.info('Getting plugins list... [manager={0}]'
                .format(management_ip))
    pt = utils.table(['id', 'uploaded_at'],
                     data=client.plugins.list())
    print_table('plugins:', pt)
