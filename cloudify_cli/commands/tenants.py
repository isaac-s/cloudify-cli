########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############

from .. import env
from ..cli import cfy
from ..table import print_data
from ..utils import handle_client_error

TENANT_COLUMNS = ['name', 'groups', 'users']


@cfy.group(name='tenants')
@cfy.options.verbose()
def tenants():
    """Handle Cloudify tenants (Premium feature)
    """
    if not env.is_initialized():
        env.raise_uninitialized()


@tenants.command(name='list',
                 short_help='List tenants [manager only]')
@cfy.options.sort_by('name')
@cfy.options.descending
@cfy.options.verbose()
@cfy.assert_manager_active()
@cfy.pass_client()
@cfy.pass_logger
def list(sort_by, descending, logger, client):
    """List all tenants
    """
    logger.info('Listing all tenants...')
    tenants_list = client.tenants.list(sort=sort_by, is_descending=descending)
    print_data(TENANT_COLUMNS, tenants_list, 'Tenants:')


@tenants.command(name='create',
                 short_help='Create a tenant [manager only]')
@cfy.argument('tenant-name')
@cfy.options.verbose()
@cfy.assert_manager_active()
@cfy.pass_client(use_tenant_in_header=False)
@cfy.pass_logger
def create(tenant_name, logger, client):
    """Create a new tenant on the manager

    `TENANT_NAME` is the name of the new tenant
    """
    client.tenants.create(tenant_name)
    logger.info('Tenant `{0}` created'.format(tenant_name))


@tenants.command(name='add-user',
                 short_help='Add a user to a tenant [manager only]')
@cfy.argument('username')
@cfy.options.tenant_name()
@cfy.options.verbose()
@cfy.assert_manager_active()
@cfy.pass_client()
@cfy.pass_logger
def add_user(username, tenant_name, logger, client):
    """Add a user to a tenant

    `USERNAME` is the name of the user to add to the tenant
    """
    graceful_msg = 'User `{0}` is already associated with ' \
                   'tenant `{1}`'.format(username, tenant_name)
    with handle_client_error(409, graceful_msg, logger):
        client.tenants.add_user(username, tenant_name)
        logger.info('User `{0}` added successfully to tenant '
                    '`{1}`'.format(username, tenant_name))


@tenants.command(name='remove-user',
                 short_help='Remove a user from a tenant [manager only]')
@cfy.argument('username')
@cfy.options.tenant_name()
@cfy.options.verbose()
@cfy.assert_manager_active()
@cfy.pass_client()
@cfy.pass_logger
def remove_user(username, tenant_name, logger, client):
    """Remove a user from a tenant

    `USERNAME` is the name of the user to remove from the tenant
    """
    graceful_msg = 'User `{0}` is not associated with ' \
                   'tenant `{1}`'.format(username, tenant_name)
    with handle_client_error(404, graceful_msg, logger):
        client.tenants.remove_user(username, tenant_name)
        logger.info('User `{0}` removed successfully from tenant '
                    '`{1}`'.format(username, tenant_name))


@tenants.command(name='add-user-group',
                 short_help='Add a user group to a tenant [manager only]')
@cfy.argument('user-group-name')
@cfy.options.tenant_name()
@cfy.options.verbose()
@cfy.assert_manager_active()
@cfy.pass_client()
@cfy.pass_logger
def add_group(user_group_name, tenant_name, logger, client):
    """Add a user group to a tenant

    `USER_GROUP_NAME` is the name of the user group to add to the tenant
    """
    graceful_msg = 'User group `{0}` is already associated with ' \
                   'tenant `{1}`'.format(user_group_name, tenant_name)
    with handle_client_error(409, graceful_msg, logger):
        client.tenants.add_group(user_group_name, tenant_name)
        logger.info('User group `{0}` added successfully to tenant '
                    '`{1}`'.format(user_group_name, tenant_name))


@tenants.command(name='remove-user-group',
                 short_help='Remove a user group from a tenant [manager only]')
@cfy.argument('user-group-name')
@cfy.options.tenant_name()
@cfy.options.verbose()
@cfy.assert_manager_active()
@cfy.pass_client()
@cfy.pass_logger
def remove_group(user_group_name, tenant_name, logger, client):
    """Remove a user group from a tenant

    `USER_GROUP_NAME` is the name of the user group to remove from the tenant
    """
    graceful_msg = 'User group `{0}` is not associated with ' \
                   'tenant `{1}`'.format(user_group_name, tenant_name)
    with handle_client_error(404, graceful_msg, logger):
        client.tenants.remove_group(user_group_name, tenant_name)
        logger.info('User group `{0}` removed successfully from tenant '
                    '`{1}`'.format(user_group_name, tenant_name))


@tenants.command(name='get',
                 short_help='Get details for a single tenant [manager only]')
@cfy.argument('tenant-name')
@cfy.options.verbose()
@cfy.assert_manager_active()
@cfy.pass_client()
@cfy.pass_logger
def get(tenant_name, logger, client):
    """Get details for a single tenant

    `TENANT_NAME` is the name of the tenant
    """
    logger.info('Getting info for tenant `{0}`...'.format(tenant_name))
    tenant_details = client.tenants.get(tenant_name)
    print_data(TENANT_COLUMNS, tenant_details, 'Requested tenant info:')


@tenants.command(name='delete',
                 short_help='Delete a tenant [manager only]')
@cfy.argument('tenant-name')
@cfy.options.verbose()
@cfy.assert_manager_active()
@cfy.pass_client()
@cfy.pass_logger
def delete(tenant_name, logger, client):
    """Delete a tenant

    `TENANT_NAME` is the name of the tenant
    """
    logger.info('Deleting tenant `{0}`...'.format(tenant_name))
    client.tenants.delete(tenant_name)
    logger.info('Tenant removed')
