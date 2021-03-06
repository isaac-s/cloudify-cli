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

import time
import threading

from cloudify import logs

from ..cli import cfy
from ..exceptions import ExecutionTimeoutError
from ..exceptions import SuppressedCloudifyCliError
from ..execution_events_fetcher import wait_for_execution, \
    WAIT_FOR_EXECUTION_SLEEP_INTERVAL

_NODE_INSTANCE_STATE_STARTED = 'started'


@cfy.group(name='agents')
@cfy.options.verbose()
@cfy.assert_manager_active()
def agents():
    """Handle a deployment's agents
    """
    pass


def _is_deployment_installed(client, deployment_id):
    for node_instance in client.node_instances.list(deployment_id):
        if node_instance.state != _NODE_INSTANCE_STATE_STARTED:
            return False
    return True


def _deployment_exists(client, deployment_id):
    try:
        client.deployments.get(deployment_id)
    except:
        return False
    return True


@agents.command(name='install',
                short_help='Install deployment agents [manager only]')
@cfy.argument('deployment-id', required=False)
@cfy.options.include_logs
@cfy.options.install_script
@cfy.options.verbose()
@cfy.pass_logger
@cfy.pass_client()
def install(deployment_id, include_logs, install_script, logger, client):
    """Install agents on the hosts of existing deployments

    `DEPLOYMENT_ID` - The ID of the deployment you would like to
    install agents for.

    See Cloudify's documentation at http://docs.getcloudify.org for more
    information.
    """
    workflow_id = 'install_new_agents'

    if deployment_id:
        deps = [deployment_id]
        if not _deployment_exists(client, deployment_id):
            logger.error("Could not find deployment for deployment id: '{0}'."
                         .format(deployment_id))
            raise SuppressedCloudifyCliError()
        if not _is_deployment_installed(client, deployment_id):
            logger.error("Deployment '{0}' is not installed"
                         .format(deployment_id))
            raise SuppressedCloudifyCliError()
        logger.info("Installing agent for deployment '{0}'"
                    .format(deployment_id))
    else:
        deps = [dep.id for dep in client.deployments.list()
                if _is_deployment_installed(client, dep.id)]
        if not deps:
            logger.error('There are no deployments installed')
            raise SuppressedCloudifyCliError()
        logger.info('Installing agents for all installed deployments')

    error_summary = []
    error_summary_lock = threading.Lock()

    event_lock = threading.Lock()

    def log_to_summary(message):
        with error_summary_lock:
            error_summary.append(message)

    def threadsafe_log(message):
        with event_lock:
            logger.info(message)

    def threadsafe_events_logger(events):
        with event_lock:
            for event in events:
                output = logs.create_event_message_prefix(event)
                if output:
                    logger.info(output)

    def worker(dep_id):
        timeout = 900

        try:
            kwargs = {}
            if install_script is not None:
                kwargs = {
                    'parameters': {
                        'install_script': install_script
                    },
                    'allow_custom_parameters': True
                }
            execution = client.executions.start(
                dep_id,
                workflow_id,
                **kwargs
            )

            execution = wait_for_execution(
                client,
                execution,
                events_handler=threadsafe_events_logger,
                include_logs=include_logs,
                timeout=timeout
            )

            if execution.error:
                log_to_summary("Execution of workflow '{0}' for "
                               "deployment '{1}' failed. [error={2}]"
                               .format(workflow_id,
                                       dep_id,
                                       execution.error))
            else:
                threadsafe_log("Finished executing workflow "
                               "'{0}' on deployment"
                               " '{1}'".format(workflow_id, dep_id))

        except ExecutionTimeoutError as e:
            log_to_summary(
                "Timed out waiting for workflow '{0}' of deployment '{1}' to "
                "end. The execution may still be running properly; however, "
                "the command-line utility was instructed to wait up to {3} "
                "seconds for its completion.\n\n"
                "* Run 'cfy executions list' to determine the execution's "
                "status.\n"
                "* Run 'cfy executions cancel --execution-id {2}' to cancel"
                " the running workflow.".format(
                    workflow_id, deployment_id, e.execution_id, timeout))

    threads = [threading.Thread(target=worker, args=(dep_id,))
               for dep_id in deps]

    for t in threads:
        t.daemon = True
        t.start()

    while True:
        if all(not thread.is_alive() for thread in threads):
            break
        time.sleep(WAIT_FOR_EXECUTION_SLEEP_INTERVAL)

    if error_summary:
        logger.error('Summary:\n{0}\n'.format(
            '\n'.join(error_summary)
        ))

        raise SuppressedCloudifyCliError()
