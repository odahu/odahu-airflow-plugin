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

from airflow.models import BaseOperator
from airflow.operators.sensors import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from odahuflow.airflow_plugin.api import OdahuHook
from odahuflow.airflow_plugin.training import XCOM_TRAINED_ARTIFACT_KEY
from odahuflow.sdk.clients.api import WrongHttpStatusCode
from odahuflow.sdk.clients.packaging import ModelPackagingClient, SUCCEEDED_STATE, FAILED_STATE
from odahuflow.sdk.models import ModelPackaging

XCOM_PACKAGING_RESULT_KEY = "packaging_result"


class PackagingOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 packaging: ModelPackaging,
                 api_connection_id: str,
                 trained_task_id: str = "",
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.packaging = packaging
        self.api_connection_id = api_connection_id
        self.trained_task_id = trained_task_id

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id
        )

    def execute(self, context):
        client: ModelPackagingClient = self.get_hook().get_api_client(ModelPackagingClient)

        try:
            if self.trained_task_id:
                artifact_name = context['task_instance'].xcom_pull(task_ids=self.trained_task_id,
                                                                   key=XCOM_TRAINED_ARTIFACT_KEY)
                print(artifact_name)
                self.packaging.spec.artifact_name = artifact_name

            if self.packaging.id:
                client.delete(self.packaging.id)
        except WrongHttpStatusCode as e:
            if e.status_code != 404:
                raise e

        train = client.create(self.packaging)

        return train.id


class PackagingSensor(BaseSensorOperator):

    @apply_defaults
    def __init__(self,
                 packaging_id: str,
                 api_connection_id: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.packaging_id = packaging_id
        self.api_connection_id = api_connection_id

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id
        )

    def poke(self, context):
        client: ModelPackagingClient = self.get_hook().get_api_client(ModelPackagingClient)

        pack_status = client.get(self.packaging_id).status

        if pack_status.state == FAILED_STATE:
            raise Exception(f'Model packaging {self.packaging_id} was failed')

        if pack_status.state == SUCCEEDED_STATE:
            results = {result.name: result.value for result in pack_status.results}

            context['task_instance'].xcom_push(XCOM_PACKAGING_RESULT_KEY, results)

            return True

        return False
