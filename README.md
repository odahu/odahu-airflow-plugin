# odahu-airflow-plugins

An apache airflow plugin for the Odahu Platform.

### How-To 

1. Start a Odahu Cluster and authenticate using OAuth2. (Hit the cluster's base URL.) Copy the token to line 8 of ./dags/odahu_dag.py
1. [Install, Start and InitDB for Airflow](https://airflow.apache.org/installation.html)  
1. Install the plugin defined in ./plugin/ to Airflow (or softlink/copy to $AIRFLOW_HOME/plugins)
1. Copy or import ./dags/odahu_dag.py
1. Create the Airflow connections:
* `odahu_model`
    * `id`: odahu_model
    * `type`: http
    * `host`: edge.cluster-name.ailifecycle.org
    * `schema`: https
* `odahu_api`
    * `id`: odahu_edi
    * `type`: http
    * `host`: odahu.cluster-name.ailifecycle.org
    * `schema`: https
    * `login`: ****
    * `password`: ****
    * `extra`: {"auth_url": "****", "client_id": "****", "client_secret": "****", "scope": "openid profile email offline_access groups"}

1. Invoke

### DEV notes

1. We need a custom Airflow Connection - or maybe [this one](https://github.com/eliiza/airflow-oauth2) will work.
