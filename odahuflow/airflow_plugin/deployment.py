#
#    Copyright 2019 EPAM Systems
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
import time

from airflow.models import BaseOperator
from airflow.operators.sensors import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from odahuflow.airflow_plugin.api import OdahuHook
from odahuflow.airflow_plugin.packaging import XCOM_PACKAGING_RESULT_KEY
from odahuflow.sdk.clients.api import WrongHttpStatusCode
from odahuflow.sdk.clients.deployment import ModelDeploymentClient, READY_STATE, FAILED_STATE
from odahuflow.sdk.models import ModelDeployment

DEFAULT_WAIT_TIMEOUT = 5


class DeploymentOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 deployment: ModelDeployment,
                 api_connection_id: str,
                 packaging_task_id: str = "",
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.deployment = deployment
        self.api_connection_id = api_connection_id
        self.packaging_task_id = packaging_task_id

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id
        )

    def execute(self, context):
        client: ModelDeploymentClient = self.get_hook().get_api_client(ModelDeploymentClient)

        try:
            if self.packaging_task_id:
                result = context['task_instance'].xcom_pull(task_ids=self.packaging_task_id,
                                                            key=XCOM_PACKAGING_RESULT_KEY)
                print(result)
                self.deployment.spec.image = result["image"]

            if self.deployment.id:
                client.delete(self.deployment.id)

                self.wait_delete_operation_finish(200, self.deployment.id, client)
        except WrongHttpStatusCode as e:
            if e.status_code != 404:
                raise e

        dep = client.create(self.deployment)

        return dep.id

    def wait_delete_operation_finish(self, timeout: int, md_id: str, md_client: ModelDeploymentClient):
        start = time.time()

        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                raise Exception('Time out: operation has not been confirmed')

            try:
                md_client.get(md_id)
            except WrongHttpStatusCode as e:
                if e.status_code == 404:
                    self.log.info(f'Model deployment {md_id} was deleted')

                    return
                self.log.info('Callback have not confirmed completion of the operation')

            self.log.info(f'Model deployment {md_id} is still being deleted...')
            time.sleep(DEFAULT_WAIT_TIMEOUT)


class DeploymentSensor(BaseSensorOperator):

    @apply_defaults
    def __init__(self,
                 deployment_id: str,
                 api_connection_id: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.deployment_id = deployment_id
        self.api_connection_id = api_connection_id

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id
        )

    def poke(self, context):
        # pylint: disable=unused-argument
        client: ModelDeploymentClient = self.get_hook().get_api_client(ModelDeploymentClient)

        dep_status = client.get(self.deployment_id).status

        if dep_status.state == FAILED_STATE:
            raise Exception(f'Deployment {self.deployment_id} was failed')

        return dep_status.state == READY_STATE
