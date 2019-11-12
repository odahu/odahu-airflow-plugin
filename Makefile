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

.PHONY: install

all: help

## install: Install airflow-plugin python package
install:
	rm -rf build dist *.egg-info && \
		pip3 install ${BUILD_PARAMS} -e . && \
		python setup.py sdist && \
		python setup.py bdist_wheel

## install-tests: Install test dependecies
install-tests:
	pip install -e ".[testing]"

## lint: Start linting
lint:
	pylint odahuflow
	pylint tests

## test: Start unit tests
test:
	pytest tests

## install-vulnerabilities-checker: Install the vulnerabilities-checker
install-vulnerabilities-checker:
	./scripts/install-git-secrets-hook.sh install_binaries

## check-vulnerabilities: Сheck vulnerabilities in the source code
check-vulnerabilities:
	./scripts/install-git-secrets-hook.sh install_hooks
	git secrets --scan -r

## help: Show the help message
help: Makefile
	@echo "Choose a command run in "$(PROJECTNAME)":"
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | sed -e 's/\\$$//' | sed -e 's/##//'
	@echo
