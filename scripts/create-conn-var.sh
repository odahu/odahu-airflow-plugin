#!/usr/bin/env bash

function Validate() {
	# Validate profile path
	if [[ ! $PROFILE ]]; then
		echo "ERROR: No PROFILE found. Pass path to the Cluster profile json file as PROFILE env var!"
		exit 1
	fi
}


# Get parameter from cluster profile
function GetParam() {
	result=$(jq -r ".$1" "${PROFILE}")
	if [[ "$result" == null ]]; then
		echo "ERROR: $1 parameter is missing in ${PROFILE} cluster profile"
		exit 1
	else
		echo "$result"
	fi
}


Validate
wine_bucket=$(GetParam 'wine_bucket')
project_id=$(GetParam 'project_id')
odahu_url=$(GetParam 'odahu_url')
test_user_email=$(GetParam 'test_user_email')
test_user_password=$(GetParam 'test_user_password')
keycloak_openid_url=$(GetParam 'keycloak_openid_url')
test_oauth_client_secret=$(GetParam 'test_oauth_client_secret')

edi_conn=$(cat $PROFILE | jq )

echo $edi_conn

## create variables
#airflow variables --set WINE_BUCKET $wine_bucket
#airflow variables --set GCP_PROJECT $project_id
#
## create connections
#airflow connections --add \
#    --conn_id odahuflow_model \
#    --conn_type http \
#    --conn_schema https \
#    --conn_host odahu.$odahu_url/service-catalog
#
#airflow connections --add \
#    --conn_id odahuflow_model \
#    --conn_type http \
#    --conn_schema https \
#    --conn_host odahu.$odahu_url/service-catalog
#
#airflow connections --add \
#    --conn_id odahuflow_api \
#    --conn_type http \
#    --conn_schema https \
#    --conn_host odahu.$odahu_url \
#    --conn_login $test_user_email \
#    --conn_password $test_user_password \
#    --conn_extra $edi_conn


