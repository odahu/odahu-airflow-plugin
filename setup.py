#!/usr/bin/env python3
#
#    Copyright 2019 EPAM Systems
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
import os
import re

from setuptools import setup, find_namespace_packages

PACKAGE_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(PACKAGE_ROOT_PATH, 'odahuflow/airflow_plugin', '__version__.py')


def extract_version() -> str:
    """
    Extract version from .py file using regex

    :return: odahuflow version
    """
    with open(VERSION_FILE, 'rt') as version_file:
        file_content = version_file.read()
        VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
        mo = re.search(VSRE, file_content, re.M)
        if mo:
            return mo.group(1)
        else:
            raise RuntimeError("Unable to find version string in %s." % (file_content,))


setup(
    name='odahu-flow-airflow-plugin',
    author='Vlad Tokarev, Vitalik Solodilov',
    author_email='vlad.tokarev.94@gmail.com, mcdkr@yandex.ru',
    license='Apache v2',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='airflow odahuflow',
    python_requires='>=3.6',
    packages=find_namespace_packages(),
    data_files=[('', ["README.md"])],
    zip_safe=False,
    entry_points={
        'airflow.plugins': [
            'odahuflow = odahuflow.airflow_plugin.plugin:OdahuPlugin'
        ]
    },
    install_requires=[
        'odahu-flow-sdk==1.0.0rc32',
        'requests>=2.22.0',
        # because this package is in conflict of odahu-flow-sdk and requests but pip doesn't have true dependency
        # resolver (https://github.com/pypa/pip/issues/988)
        'urllib3>=1.24.3'
    ],
    extras_require={
        'testing': [
            'pytest>=5.1.2',
            'pytest-mock>=1.10.4',
            'pytest-cov>=2.7.1',
            'pylint>=2.3.0',
            'apache-airflow==1.10.2',
            'google-api-python-client'
        ]
    },
    version=extract_version(),
)
