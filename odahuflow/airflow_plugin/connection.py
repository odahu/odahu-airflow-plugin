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

from airflow.models import BaseOperator, Connection as AirflowConnection
from airflow.utils.decorators import apply_defaults
from odahuflow.airflow_plugin.api import OdahuHook
from odahuflow.sdk.clients.api import WrongHttpStatusCode
from odahuflow.sdk.clients.connection import ConnectionClient
from odahuflow.sdk.models import Connection

GCP_CREDENTIALS_KEYFILE_DICT = "extra__google_cloud_platform__keyfile_dict"


class GcpConnectionToOdahuConnectionOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 api_connection_id: str,
                 google_cloud_storage_conn_id: str,
                 conn_template: Connection,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.conn_template = conn_template
        self.api_connection_id = api_connection_id
        self.google_cloud_storage_conn_id = google_cloud_storage_conn_id

    def get_hook(self) -> OdahuHook:
        return OdahuHook(
            self.api_connection_id
        )

    def execute(self, context):
        gcp_conn: AirflowConnection = self.get_hook().get_connection(self.google_cloud_storage_conn_id)
        self.conn_template.spec.key_secret = gcp_conn.extra_dejson[GCP_CREDENTIALS_KEYFILE_DICT]
        client: ConnectionClient = self.get_hook().get_api_client(ConnectionClient)

        try:
            if self.conn_template.id:
                client.delete(self.conn_template.id)
        except WrongHttpStatusCode as e:
            if e.status_code != 404:
                raise e

        conn = client.create(self.conn_template)

        self.log.info(conn)
