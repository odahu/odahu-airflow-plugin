#!/bin/bash
set -e

PYLINT_FOLDER="target/pylint"
PYDOCSTYLE_FOLDER="target/pydocstyle"

function pylint_cmd() {
    pylint --output-format=parseable \
           ${additional_pylint_args} \
           --reports=no . 2>&1 | tee "${PYLINT_FOLDER}/legion-airflow.log" &
}

rm -rf "${PYLINT_FOLDER}"
mkdir -p "${PYLINT_FOLDER}"

pylint_cmd .

function pydocstyle_cmd() {
    pydocstyle --ignore D301 \
               --match-dir '^(?!models).*' \
               --source . 2>&1 | tee "${PYDOCSTYLE_FOLDER}/legion-airflow.log" &
}

rm -rf "${PYDOCSTYLE_FOLDER}"
mkdir -p "${PYDOCSTYLE_FOLDER}"

pydocstyle_cmd

FAIL=0
# Wait all background linters
for job in `jobs -p`
do
echo $job
    echo "waiting..."
    wait $job || let "FAIL+=1"
done

cat "${PYDOCSTYLE_FOLDER}/legion-airflow.log"
cat "${PYLINT_FOLDER}/legion-airflow.log"
echo "You can find the result of linting here: ${PYLINT_FOLDER} and ${PYDOCSTYLE_FOLDER}"

if [[ "$FAIL" != "0" ]];
then
    echo "Failed $FAIL linters"
    exit 1
fi
