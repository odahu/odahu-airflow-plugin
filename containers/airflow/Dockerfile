ARG AIRFLOW_VERSION="2.2.1"
FROM apache/airflow:${AIRFLOW_VERSION}-python3.6

ARG AIRFLOW_USER_HOME=/home/airflow
ARG PIP_EXTRA_INDEX_URL=""
ARG PYTHON_DEPS=""
ARG AIRFLOW_DEPS=""

RUN mkdir ${AIRFLOW_USER_HOME}/.config

COPY containers/airflow/airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg
COPY containers/airflow/pip.conf ${AIRFLOW_USER_HOME}/.config/pip.conf
COPY containers/airflow/health_check.py /home/airflow/.local/lib/python3.6/site-packages/airflow/example_dags/

RUN sed -i "s|PIP_EXTRA_INDEX_URL|${PIP_EXTRA_INDEX_URL}|" ${AIRFLOW_USER_HOME}/.config/pip.conf \
 && rm /home/airflow/.local/lib/python3.6/site-packages/airflow/example_dags/t*.py \
 && rm /home/airflow/.local/lib/python3.6/site-packages/airflow/example_dags/example*.py \
 && pip install --user --upgrade pip setuptools wheel \
 && if [ -n "${AIRFLOW_DEPS}" ]; then pip install --user apache-airflow[${AIRFLOW_DEPS}]==${AIRFLOW_VERSION}; fi \
 && if [ -n "${PYTHON_DEPS}" ]; then pip install --user ${PYTHON_DEPS}; fi
