SHELL := /bin/bash

AIRFLOW_GPL_UNIDECODE=yes
PROJECTNAME := $(shell basename "$(PWD)")

PYLINT_FOLDER=target/pylint
PYDOCSTYLE_FOLDER=target/pydocstyle
PROJECTS_PYLINT=sdk cli tests
PROJECTS_PYCODESTYLE="sdk cli"

BUILD_PARAMS=

CREDENTIAL_SECRETS=.secrets.yaml

BUILD_TAG=latest
TAG=
# Example of DOCKER_REGISTRY: nexus.domain.com:443/
DOCKER_REGISTRY=

GOOGLE_APPLICATION_CREDENTIALS=

HIERA_KEYS_DIR=
LEGION_PROFILES_DIR=

CLUSTER_NAME=
CLOUD_PROVIDER=

EXPORT_HIERA_DOCKER_IMAGE := legion/k8s-terraform:${BUILD_TAG}
SECRET_DIR := $(CURDIR)/.secrets
CLUSTER_PROFILE := ${SECRET_DIR}/cluster_profile.json

-include .env

.EXPORT_ALL_VARIABLES:

.PHONY: install-all

all: help

## install-all: Install all python packages
install-all: download-dependencies install-legion-airflow-plugin

## download-dependencies: Download plugin dependencies
download-dependencies:
	pipenv install --system --dev

## install-sdk: Install airflow-plugin python package
install-legion-airflow-plugin:
	rm -rf build dist *.egg-info && \
	pip3 install ${BUILD_PARAMS} -e . && \
	python setup.py sdist && \
	python setup.py bdist_wheel

## docker-build-pipeline-agent: Build pipeline agent docker image
docker-build-pipeline-agent:
	docker build -t legion/legion-airlflow-pipeline-agent:${BUILD_TAG} -f containers/pipeline-agent/Dockerfile .

## docker-build-all: Build all docker images
docker-build-all:  docker-build-pipeline-agent

## lint: Lints source code
lint:
	scripts/lint.sh

# TODO: implement soon
## unittests: Run unit tests
unittests:
	exit 1
	mkdir -p target
	mkdir -p target/cover
	DEBUG=true VERBOSE=true pytest \
	          --cov=legion \
	          --cov-report xml:target/legion-cover.xml \
	          --cov-report html:target/cover \
	          --cov-report term-missing \
	          --junitxml=target/nosetests.xml \
	          .

## update-python-deps: Update all python dependecies in the Pipfiles
update-python-deps:
	pipenv update

define verify_existence
	@if [ "${$(1)}" == "" ]; then \
	    echo "$(1) is not found, please define the $(1) variable" ; exit 1 ;\
	fi
endef

## export-hiera: Export hiera data
export-hiera:
	set -e
	$(call verify_existence,CLUSTER_NAME)
	$(call verify_existence,HIERA_KEYS_DIR)
	$(call verify_existence,SECRET_DIR)
	$(call verify_existence,CLOUD_PROVIDER)
	$(call verify_existence,EXPORT_HIERA_DOCKER_IMAGE)
	$(call verify_existence,LEGION_PROFILES_DIR)

	mkdir -p ${SECRET_DIR}
	docker run \
	           --net host \
	           -v ${HIERA_KEYS_DIR}:/opt/legion/.hiera_keys \
	           -v ${LEGION_PROFILES_DIR}:/opt/legion/legion-profiles \
	           -v ${SECRET_DIR}:/opt/legion/.secrets \
	           -e CLUSTER_NAME=${CLUSTER_NAME} \
	           -e CLOUD_PROVIDER=${CLOUD_PROVIDER} \
	           ${EXPORT_HIERA_DOCKER_IMAGE} hiera_exporter_helper

## help: Show the help message
help: Makefile
	@echo "Choose a command run in "$(PROJECTNAME)":"
	@sed -n 's/^##//p' $< | column -t -s ':' |  sed -e 's/^/ /'
	@echo
