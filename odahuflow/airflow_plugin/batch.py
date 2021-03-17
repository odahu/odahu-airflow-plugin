#
#      Copyright 2021 EPAM Systems
#
#      Licensed under the Apache License, Version 2.0 (the "License");
#      you may not use this file except in compliance with the License.
#      You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#      Unless required by applicable law or agreed to in writing, software
#      distributed under the License is distributed on an "AS IS" BASIS,
#      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#      See the License for the specific language governing permissions and
#      limitations under the License.

import logging

from airflow.models import BaseOperator
from airflow.operators.sensors import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from odahuflow.sdk.clients.api import EntityAlreadyExists
from odahuflow.sdk.clients.batch_job import BatchInferenceJobClient, InferenceJob, SUCCESS_STATE, FAILED_STATE
from odahuflow.sdk.clients.batch_service import InferenceService, BatchInferenceServiceClient

from odahuflow.airflow_plugin.api import OdahuHook


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

XCOM_BATCH_ARTIFACT_KEY = "batch_job_id"


class InferenceServiceOperator(BaseOperator):
    @apply_defaults
    def __init__(self,
                 service: InferenceService,
                 api_connection_id: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.service = service
        self.api_connection_id = api_connection_id

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id
        )

    def execute(self, context):
        # pylint: disable=unused-argument
        client: BatchInferenceServiceClient = self.get_hook().get_api_client(BatchInferenceServiceClient)

        try:
            service = client.create(self.service)
        except EntityAlreadyExists:
            logger.info(f"InferenceService is already created. id: {self.service.id}")
            return self.service.id

        logger.info(f"InferenceService was created. id: {service.id}")
        return service.id


class InferenceJobOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 job: InferenceJob,
                 api_connection_id: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.job = job
        self.api_connection_id = api_connection_id

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id
        )

    def execute(self, context):
        # pylint: disable=unused-argument
        client: BatchInferenceJobClient = self.get_hook().get_api_client(BatchInferenceJobClient)

        batch = client.create(self.job)

        logger.info(f"InferenceJob was created. id: {batch.id}")
        return batch.id


class InferenceJobSensor(BaseSensorOperator):

    @apply_defaults
    def __init__(self,
                 inference_job_task_id: str,
                 api_connection_id: str,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.inference_job_task_id = inference_job_task_id
        self.api_connection_id = api_connection_id

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id
        )

    def poke(self, context):
        client: BatchInferenceJobClient = self.get_hook().get_api_client(BatchInferenceJobClient)

        batch_id = context['task_instance'].xcom_pull(task_ids=self.inference_job_task_id)

        logger.info(f"Try to check state of Inference job {batch_id}")

        job_status = client.get(batch_id).status

        if job_status.state == FAILED_STATE:
            raise Exception(f'Inference job {batch_id} was failed')

        if job_status.state == SUCCESS_STATE:
            logger.info(f"Inference job {batch_id} was succeeded with "
                        f"state {job_status.state} and message {job_status.message}")

            return True

        return False
