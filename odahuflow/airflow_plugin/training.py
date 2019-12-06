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
from odahuflow.sdk.clients.api import WrongHttpStatusCode
from odahuflow.sdk.clients.training import ModelTrainingClient, TRAINING_SUCCESS_STATE, TRAINING_FAILED_STATE
from odahuflow.sdk.models import ModelTraining

XCOM_TRAINED_ARTIFACT_KEY = "trained_artifact_name"


class TrainingOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 training: ModelTraining,
                 api_connection_id: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.training = training
        self.api_connection_id = api_connection_id

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id
        )

    def execute(self, context):
        # pylint: disable=unused-argument
        client: ModelTrainingClient = self.get_hook().get_api_client(ModelTrainingClient)

        try:
            if self.training.id:
                client.delete(self.training.id)
        except WrongHttpStatusCode as e:
            if e.status_code != 404:
                raise e

        train = client.create(self.training)

        return train.id


class TrainingSensor(BaseSensorOperator):

    @apply_defaults
    def __init__(self,
                 training_id: str,
                 api_connection_id: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.training_id = training_id
        self.api_connection_id = api_connection_id

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id
        )

    def poke(self, context):
        client: ModelTrainingClient = self.get_hook().get_api_client(ModelTrainingClient)

        train_status = client.get(self.training_id).status

        if train_status.state == TRAINING_FAILED_STATE:
            raise Exception(f'Model training {self.training_id} was failed')

        if train_status.state == TRAINING_SUCCESS_STATE:
            context['task_instance'].xcom_push(key=XCOM_TRAINED_ARTIFACT_KEY,
                                               value=train_status.artifacts[-1].artifact_name)

            return True

        return False
