#!/usr/bin/bash
# Rajiv Gangadharan 2021-08-31
# Purpose to schedule the data pull using cron

. ./pgfetchdatasets.env
BASE_DIR=/disks/app/juka/pg
LOCK_FILE=${BASE_DIR}/.pgfetchdataset.lock
LOG_FILE=${BASE_DIR}/pgfetchdataset.lastrun.log
if [ -f ./pgfetchdatasets.env ]; then
        . ./pgfetchdatasets.env
else
        . ${BASE_DIR}/.pgfetchdatasets.env
fi


if [ -f ${LOCK_FILE} ]; then
        echo "Lock file exists, the last run did not finish. exiting."
        exit 100
else
        touch $LOCK_FILE
        python3 ${BASE_DIR}/pgfetchdataset.py --config ${BASE_DIR}/pgfetchdataset.yaml > ${LOG_FILE} 2>&1
        cat ${LOG_FILE}
        rm -f $LOCK_FILE
fi
