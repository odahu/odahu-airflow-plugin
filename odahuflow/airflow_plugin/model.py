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

import typing

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from odahuflow.sdk.clients.model import ModelClient

from odahuflow.airflow_plugin.api import OdahuHook


class ModelPredictRequestOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 model_deployment_name: str,
                 api_connection_id: str,
                 model_connection_id: str,
                 request_body: typing.Any,
                 md_role_name: str = "",
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model_deployment_name = model_deployment_name
        self.request_body = request_body
        self.model_connection_id = model_connection_id
        self.api_connection_id = api_connection_id
        self.md_role_name = md_role_name

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id,
            self.model_connection_id
        )

    def execute(self, context):
        # pylint: disable=unused-argument
        model_client: ModelClient = self.get_hook().get_model_client(self.model_deployment_name)

        resp = model_client.invoke(**self.request_body)
        print(resp)

        return resp


class ModelInfoRequestOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 model_deployment_name: str,
                 api_connection_id: str,
                 model_connection_id: str,
                 md_role_name: str = "",
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model_deployment_name = model_deployment_name
        self.model_connection_id = model_connection_id
        self.api_connection_id = api_connection_id
        self.md_role_name = md_role_name

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id,
            self.model_connection_id
        )

    def execute(self, context):
        # pylint: disable=unused-argument
        model_client: ModelClient = self.get_hook().get_model_client(self.model_deployment_name)

        resp = model_client.info()
        print(resp)

        return resp
