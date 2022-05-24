#!/usr/bin/bash
# Rajiv Gangadharan 2021-08-31
# Purpose to schedule the data pull using cron


# Passing the base directory as a command line option
function usage {
        echo "Usage $(basename) [-h] [-d dirname] "
        echo "./$(basename $0) -h --> shows usage"
        echo "./$(basename $0) -d dirname --> sets the base directory"
        echo "./$(basename $0) -f -d dirname --> forcing the run overrides locking"
}

if [[ ${#} -eq 0 ]]; then
        usage
        exit 1
fi
optstring=":hfd:"
while getopts ${optstring} arg; do
        case ${arg} in 
                h)
                        usage
                        exit 1
                        ;;
                f)
                        echo "WARNING!! Forcing the run, flag set."
                        FORCE_RUN=1
                        ;;
                d)
                        BASE_DIR=${OPTARG}
                        echo "Base Dir $OPTARG assigned."
                        ;;
                c)
                        AUTH_CONFIG_FILE=${OPTARG}
                        echo "AUTH_CONFIG_FILE is set to $OPTARG."
                        ;;
                ?)
                        echo "Invalid parameter: -${OPTARG}."
                        usage
                        echo
                        exit 1
                        ;;
        esac                
done
echo "Using ${BASE_DIR} as BASE_DIR"
if [ -f "${BASE_DIR}/pgfetchdatasets.env" ]; then
        echo -n "Environment is being setup.."
        . "${BASE_DIR}/pgfetchdatasets.env"
        echo "Done."
else
	echo "Environment setup failed from current directory."
	exit 100
fi

LOCK_FILE="${BASE_DIR}/.pgfetchdatasets.lock"
LOG_FILE="${BASE_DIR}/pgfetchdatasets.lastrun.log"
AUTH_CONFIG_FILE=${AUTH_CONFIG_FILE:-"${BASE_DIR}/pgconfig.yaml"}

function data_pull {
        if [ -f "${LOCK_FILE}" ]; then
                echo "data_pull - Lock ${LOCK_FILE} file exists, the last run did not finish"
                return 1
        else
                touch "${LOCK_FILE}"
        fi
        
        if [[ $? -ne 0 ]]; then
                echo "Error locking this execution. Exiting..."
                exit 1
        fi
        if [ -f "${BASE_DIR}/../../juka-env/bin/activate" ]; then
                source "${BASE_DIR}/../../juka-env/bin/activate"
                python "${BASE_DIR}/pgfetchdatasets.py" --config "${BASE_DIR}/pgfetchdatasets.yaml" --auth-config ${AUTH_CONFIG_FILE}> "${LOG_FILE}" 2>&1
                if [[ $? -eq 0 ]]; then
                        cat "${LOG_FILE}"
                        rm -f "${LOCK_FILE}"
                        exit 0
                else
                        SUCCESS=0
                        echo "Data pull failed."
                        cat "${LOG_FILE}"
                        exit 1
                fi
                
        else
                echo "Environment activation failed, aborting."
                echo -n "Count not run --> "
                echo "${BASE_DIR}/../../juka-env/bin/activate"
                exit 200
        fi
}

if [ -f "${LOCK_FILE}" ]; then
        echo "Lock ${LOCK_FILE} file exists, the last run did not finish."
        if [[ ${FORCE_RUN} -eq 1 ]]; then
                echo "Forcing run, force flag set, removing lock file."
                rm -f "${LOCK_FILE}"
                echo -n "Executing data pull..."
                data_pull
                echo "Done"
        else
                exit 100
        fi
else
        echo -n "Executing data pull..."
        data_pull
        echo "Done"
fi

