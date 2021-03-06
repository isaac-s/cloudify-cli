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

from ..table import print_data
from .. import utils
from ..cli import helptexts, cfy

SNAPSHOT_COLUMNS = ['id', 'created_at', 'status', 'error', 'permission'
                    'tenant_name']


@cfy.group(name='snapshots')
@cfy.options.verbose()
@cfy.assert_manager_active()
def snapshots():
    """Handle manager snapshots
    """
    pass


@snapshots.command(name='restore',
                   short_help='Restore a manager from a snapshot '
                   '[manager only]')
@cfy.argument('snapshot-id')
@cfy.options.without_deployment_envs
@cfy.options.force(help=helptexts.FORCE_RESTORE_ON_DIRTY_MANAGER)
@cfy.options.tenant_name(required=False,
                         help=helptexts.RESTORE_SNAPSHOT_TENANT_NAME)
@cfy.options.verbose()
@cfy.pass_client()
@cfy.pass_logger
def restore(snapshot_id,
            without_deployment_envs,
            force,
            tenant_name,
            logger,
            client):
    """Restore a manager to its previous state

    `SNAPSHOT_ID` is the id of the snapshot to use for restoration.
    """
    logger.info('Restoring snapshot {0}...'.format(snapshot_id))
    recreate_deployments_envs = not without_deployment_envs
    execution = client.snapshots.restore(
        snapshot_id,
        recreate_deployments_envs,
        force,
        tenant_name
    )
    logger.info("Started workflow execution. The execution's id is {0}".format(
        execution.id))


@snapshots.command(name='create',
                   short_help='Create a snapshot [manager only]')
@cfy.argument('snapshot-id', required=False)
@cfy.options.include_metrics
@cfy.options.exclude_credentials
@cfy.options.private_resource
@cfy.options.verbose()
@cfy.options.tenant_name(required=False)
@cfy.pass_client()
@cfy.pass_logger
def create(snapshot_id,
           include_metrics,
           exclude_credentials,
           private_resource,
           logger,
           client,
           tenant_name):
    """Create a snapshot on the manager

    The snapshot will contain the relevant data to restore a manager to
    its previous state.

    `SNAPSHOT_ID` is the id to attach to the snapshot.
    """
    if tenant_name:
        logger.info('Explicitly using tenant `{0}`'.format(tenant_name))
    snapshot_id = snapshot_id or utils.generate_suffixed_id('snapshot')
    logger.info('Creating snapshot {0}...'.format(snapshot_id))

    execution = client.snapshots.create(snapshot_id,
                                        include_metrics,
                                        not exclude_credentials,
                                        private_resource)
    logger.info("Started workflow execution. The execution's id is {0}".format(
        execution.id))


@snapshots.command(name='delete',
                   short_help='Delete a snapshot [manager only]')
@cfy.argument('snapshot-id')
@cfy.options.verbose()
@cfy.options.tenant_name(required=False)
@cfy.pass_client()
@cfy.pass_logger
def delete(snapshot_id, logger, client, tenant_name):
    """Delete a snapshot from the manager

    `SNAPSHOT_ID` is the id of the snapshot to download.
    """
    if tenant_name:
        logger.info('Explicitly using tenant `{0}`'.format(tenant_name))
    logger.info('Deleting snapshot {0}...'.format(snapshot_id))
    client.snapshots.delete(snapshot_id)
    logger.info('Snapshot deleted successfully')


@snapshots.command(name='upload',
                   short_help='Upload a snapshot [manager only]')
@cfy.argument('snapshot_path')
@cfy.options.snapshot_id
@cfy.options.private_resource
@cfy.options.verbose()
@cfy.options.tenant_name(required=False)
@cfy.pass_client()
@cfy.pass_logger
def upload(snapshot_path,
           snapshot_id,
           private_resource,
           logger,
           client,
           tenant_name):
    """Upload a snapshot to the manager

    `SNAPSHOT_PATH` is the path to the snapshot to upload.
    """
    if tenant_name:
        logger.info('Explicitly using tenant `{0}`'.format(tenant_name))
    snapshot_id = snapshot_id or utils.generate_suffixed_id('snapshot')

    logger.info('Uploading snapshot {0}...'.format(snapshot_path))
    progress_handler = utils.generate_progress_handler(snapshot_path, '')
    snapshot = client.snapshots.upload(snapshot_path,
                                       snapshot_id,
                                       private_resource,
                                       progress_handler)
    logger.info("Snapshot uploaded. The snapshot's id is {0}".format(
        snapshot.id))


@snapshots.command(name='download',
                   short_help='Download a snapshot [manager only]')
@cfy.argument('snapshot-id')
@cfy.options.output_path
@cfy.options.verbose()
@cfy.options.tenant_name(required=False)
@cfy.pass_client()
@cfy.pass_logger
def download(snapshot_id, output_path, logger, client, tenant_name):
    """Download a snapshot from the manager

    `SNAPSHOT_ID` is the id of the snapshot to download.
    """
    if tenant_name:
        logger.info('Explicitly using tenant `{0}`'.format(tenant_name))
    logger.info('Downloading snapshot {0}...'.format(snapshot_id))
    snapshot_name = output_path if output_path else snapshot_id
    progress_handler = utils.generate_progress_handler(snapshot_name, '')
    target_file = client.snapshots.download(snapshot_id,
                                            output_path,
                                            progress_handler)
    logger.info('Snapshot downloaded as {0}'.format(target_file))


@snapshots.command(name='list',
                   short_help='List snapshots [manager only]')
@cfy.options.sort_by()
@cfy.options.descending
@cfy.options.tenant_name(required=False)
@cfy.options.all_tenants
@cfy.options.verbose()
@cfy.pass_client()
@cfy.pass_logger
def list(sort_by, descending, tenant_name, all_tenants, logger, client):
    """List all snapshots on the manager
    """
    if tenant_name:
        logger.info('Explicitly using tenant `{0}`'.format(tenant_name))
    logger.info('Listing snapshots...')
    snapshots = client.snapshots.list(sort=sort_by,
                                      is_descending=descending,
                                      _all_tenants=all_tenants)

    print_data(SNAPSHOT_COLUMNS, snapshots, 'Snapshots:')


@snapshots.command(name='add-permission',
                   short_help='Add permissions to users')
@cfy.argument('snapshot-id')
@cfy.options.users
@cfy.options.permission
@cfy.options.verbose()
@cfy.options.tenant_name(required=False)
@cfy.assert_manager_active()
@cfy.pass_client()
@cfy.pass_logger
def add_permission(snapshot_id,
                   users,
                   permission,
                   client,
                   logger,
                   tenant_name):
    """Add `viewer`/`owner` permissions to users on a certain snapshot

    `SNAPSHOT_ID` is the ID of the snapshot to set permissions on
    """
    if tenant_name:
        logger.info('Explicitly using tenant `{0}`'.format(tenant_name))
    logger.info('Adding permission `{0}`...'.format(permission))
    client.snapshots.add_permission(snapshot_id, users, permission)
    logger.info('Permissions updated for snapshot `{0}`'.format(snapshot_id))


@snapshots.command(name='remove-permission',
                   short_help='Remove permissions from users')
@cfy.argument('snapshot-id')
@cfy.options.users
@cfy.options.permission
@cfy.options.verbose()
@cfy.options.tenant_name(required=False)
@cfy.assert_manager_active()
@cfy.pass_client()
@cfy.pass_logger
def remove_permission(snapshot_id,
                      users,
                      permission,
                      client,
                      logger,
                      tenant_name):
    """Remove `viewer`/`owner` permissions from users on a certain snapshot

    `SNAPSHOT_ID` is the ID of the snapshot to set permissions on
    """
    if tenant_name:
        logger.info('Explicitly using tenant `{0}`'.format(tenant_name))
    logger.info('Removing permission `{0}`...'.format(permission))
    client.snapshots.remove_permission(snapshot_id, users, permission)
    logger.info('Permissions updated for snapshot `{0}`'.format(snapshot_id))
