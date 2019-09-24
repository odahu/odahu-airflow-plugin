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

from legion.airflow.connection import GcpConnectionToLegionConnectionOperator
from legion.airflow.deployment import DeploymentOperator, DeploymentSensor
from legion.airflow.edi import LegionHook
from legion.airflow.model import ModelPredictRequestOperator, ModelInfoRequestOperator
from legion.airflow.packaging import PackagingOperator, PackagingSensor
from legion.airflow.training import TrainingOperator, TrainingSensor


class LegionPlugin(AirflowPlugin):
    name = 'legion'
    operators = [TrainingOperator, DeploymentOperator, PackagingOperator, ModelPredictRequestOperator,
                 ModelInfoRequestOperator, GcpConnectionToLegionConnectionOperator]
    hooks = [LegionHook]
    sensors = [TrainingSensor, DeploymentSensor, PackagingSensor]
