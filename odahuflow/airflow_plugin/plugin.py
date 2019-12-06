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

from airflow.plugins_manager import AirflowPlugin

from odahuflow.airflow_plugin.connection import GcpConnectionToOdahuConnectionOperator
from odahuflow.airflow_plugin.deployment import DeploymentOperator, DeploymentSensor
from odahuflow.airflow_plugin.api import OdahuHook
from odahuflow.airflow_plugin.model import ModelPredictRequestOperator, ModelInfoRequestOperator
from odahuflow.airflow_plugin.packaging import PackagingOperator, PackagingSensor
from odahuflow.airflow_plugin.training import TrainingOperator, TrainingSensor


class OdahuPlugin(AirflowPlugin):
    name = 'odahuflow'
    operators = [TrainingOperator, DeploymentOperator, PackagingOperator, ModelPredictRequestOperator,
                 ModelInfoRequestOperator, GcpConnectionToOdahuConnectionOperator]
    hooks = [OdahuHook]
    sensors = [TrainingSensor, DeploymentSensor, PackagingSensor]
