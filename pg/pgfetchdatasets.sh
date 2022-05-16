#!/usr/bin/bash
# Rajiv Gangadharan 2021-08-31
# Purpose to schedule the data pull using cron

if [ -f ./pgfetchdatasets.env ]; then
. ./pgfetchdatasets.env
else
	echo "Environment setup failed from current directory."
	echo "Carrying on..."
fi
echo "Using ${BASE_DIR} as BASE_DIR"
BASE_DIR="${BASE_DIR}"
LOCK_FILE="${BASE_DIR}/.pgfetchdatasets.lock"
LOG_FILE="${BASE_DIR}/pgfetchdatasets.lastrun.log"

if [ -f ./pgfetchdatasets.env ]; then
        . ./pgfetchdatasets.env
else
        . "${BASE_DIR}/.pgfetchdatasets.env"
fi

if [ -f "${LOCK_FILE}" ]; then
        echo "Lock file exists, the last run did not finish. exiting."
        exit 100
else
        touch "${LOCK_FILE}"
        if [ $? -ne 0 ]; then
                echo "Error locking this execution. Exiting..."
                exit 1
        fi
        if [ -f "${BASE_DIR}/../../juka-env/bin/activate" ]; then
                source ${BASE_DIR}/../../juka-env/bin/activate
                python "${BASE_DIR}/pgfetchdatasets.py" --config "${BASE_DIR}/pgfetchdatasets.yaml" > "${LOG_FILE}" 2>&1
                cat "${LOG_FILE}"
                rm -f "${LOCK_FILE}"
                exit 0
        else
                echo "Environment activation failed."
                exit 200
        fi
        
fi