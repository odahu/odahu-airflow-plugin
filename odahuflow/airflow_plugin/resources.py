"""
This module provide API to build odahu models (ModelTraining, ModelConnection, etc.) from yaml/json files
"""
import logging
import os
from io import StringIO
from typing import Union, Tuple

from airflow import settings
from odahuflow.sdk.clients.api_aggregated import OdahuflowCloudResourceUpdatePair, parse_stream

logger = logging.getLogger(__name__)


def _find_absolute_resource_file(path: str) -> Union[str, None]:
    """
    Try to find absolute path for resource file
    :param path: str relative path to (the most foreground is top):
        * Airflow DAGs
        * Airflow HOME
    :return: absolute path as :str if file exists otherwise `None`
    """

    base_paths = [settings.DAGS_FOLDER, settings.AIRFLOW_HOME]

    for bp in base_paths:
        abs_path = os.path.join(bp, path)
        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            return abs_path


def _build_resource_body(path_or_body: str, **template_vars) -> Tuple[str, Union[str, None]]:
    """
    1. If path_or_body is a valid filepath to odahu resource YAML/JSON file then it loads its content
    2. If path_or_body is a YAML/JSON string that describe odahu resource then it handles it as is
    3. Render content as `path_or_body.format(**template_vars)`

    :param path_or_body: could be
        * a relative filepath to DAGs or HOME Airflow folders to odahu resource YAML/JSON file
        * a YAML/JSON string that describe Odahu resource
    :param template_vars: variables that could be used to render resource body (if it contains bracket rounded pieces)
    :return: Odahu resource body as a YAML/JSON string and absolute filepath to definition file
    if this body was read from file (otherwise None)
    """

    abs_path_to_resource_file = _find_absolute_resource_file(path_or_body)

    if abs_path_to_resource_file:
        with open(abs_path_to_resource_file, 'r') as data_stream:
            resource_body_tpl = data_stream.read()
    else:
        resource_body_tpl = path_or_body

    try:
        resource_body = resource_body_tpl.format(**template_vars)
    except KeyError as exc_info:
        raise KeyError('Not all template variables in payload have values. '
                       'Please pass values for all vars as keyword arguments') from exc_info

    return resource_body, abs_path_to_resource_file


def _parse_resource_body(resource_body: str) -> OdahuflowCloudResourceUpdatePair:
    """
    Build `OdahuflowCloudResourceUpdatePair` from YAML/JSON content string
    :param resource_body:  YAML/JSON odahu resource definition
    :return: OdahuflowCloudResourceUpdatePair
    """

    resources = parse_stream(StringIO(resource_body))

    resources_len = len(resources.changes)
    if resources_len != 1:
        raise TypeError(f'Resource definition contains {resources_len} entities but must contains exactly one')

    resource_pair: OdahuflowCloudResourceUpdatePair = resources.changes[0]

    return resource_pair


def resource(path_or_body: str, **template_vars) -> OdahuflowCloudResourceUpdatePair:
    """
    Create `OdahuflowCloudResourceUpdatePair` object from resource definition in YAML/JSON format.
    Resource definition could be passed as a string in `path_or_body` OR a filepath to a valid YAML/JSON file.
    :param path_or_body: could be
        * a relative filepath to DAGs or HOME Airflow folders to odahu resource YAML/JSON file
        * a YAML/JSON string that describe Odahu resource
    :param template_vars: variables that could be used to render resource body (if it contains bracket rounded pieces)
    :return: OdahuflowCloudResourceUpdatePair with resource that was build from resource definition
    """

    resource_body, fp = _build_resource_body(path_or_body, **template_vars)

    pair = _parse_resource_body(resource_body)

    logger.info(f'Resource {pair.resource} was initialized from {"string" if fp is None else fp}')

    return pair
