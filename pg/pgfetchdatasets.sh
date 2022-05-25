#!/usr/bin/bash
# Rajiv Gangadharan 2021-08-31
# Purpose to schedule the data pull using cron
# Passing the base directory as a command line option

function usage {
        echo "Usage ./$(basename) [-h] [-d dirname] "
        echo "./$(basename $0) -h - shows usage"
        echo "./$(basename $0) -d dirname - sets the base directory"
        echo "./$(basename $0) -f -d dirname - force flag, overrides locking"
        echo "./$(basename $0) -d dirname [-l log-file] [-a auth-config-file] [-c config-file] [-e env-file]"
}

if [[ ${#} -eq 0 ]]; then
        usage
        exit 1
fi

optstring=":hfd:l:c:a:e:"
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
                a)
                        AUTH_CONFIG_FILE=${OPTARG}
                        echo "AUTH_CONFIG_FILE is set to $OPTARG."
                        ;;
                c)
                        CONFIG_FILE=${OPTARG}
                        echo "CONFIG_FILE is set to $OPTARG."
                        ;;
                e)
                        ENV_FILE=${OPTARG}
                        echo "ENV_FILE is set to $OPTARG."
                        ;;
                l)
                        LOG_FILE=${OPTARG}
                        echo "LOG_FILE is set to $OPTARG."
                        ;;
                ?)
                        echo "Invalid parameter: -${OPTARG}."
                        usage
                        echo
                        exit 1
                        ;;
        esac                
done
LOCK_FILE=${LOCK_FILE:-"${BASE_DIR}/.pgfetchdatasets.lock"}
LOG_FILE=${LOG_FILE:-"${BASE_DIR}/pgfetchdatasets.lastrun.log"}
AUTH_CONFIG_FILE=${AUTH_CONFIG_FILE:-"${BASE_DIR}/pgconfig.yaml"}
ENV_FILE=${ENV_FILE:-"${BASE_DIR}/../../juka-env/bin/activate"}
CONFIG_FILE=${CONFIG_FILE:-"${BASE_DIR}/pgfetchdatasets.yaml"}

echo " ===========  RUN PARAMETERS =========="
echo "Env file ${ENV_FILE}"
echo "Base dir ${BASE_DIR}"
echo "Config file ${CONFIG_FILE}"
echo " ======================================"

echo "Using ${BASE_DIR} as BASE_DIR"

function setup_local_env {
        if [ -f "${BASE_DIR}/pgfetchdatasets.env" ]; then
                echo -n "Local environment is being setup, if env file present.."
                . "${BASE_DIR}/pgfetchdatasets.env"
                echo "Done."
        fi
}

function lock_execution {
        if [ -f "${LOCK_FILE}" ]; then
                echo "Lock ${LOCK_FILE} file exists, the last run did not finish"
                return 1
        else
                echo "Locking run, creating lock file ${LOCK_FILE}"
                touch "${LOCK_FILE}"
        fi
        
        if [[ $? -ne 0 ]]; then
                echo "Error locking this execution, returning zero."
                return 0
        fi
}

function data_pull {
        if [ -f ${ENV_FILE} ]; then
                echo "Setting up python environment, executing ${ENV_FILE}"
                source "${ENV_FILE}"
                python "${BASE_DIR}/pgfetchdatasets.py" --config "${CONFIG_FILE}" --auth-config "${AUTH_CONFIG_FILE}" --log-file "${LOG_FILE}"
                if [[ $? -eq 0 ]]; then
                        echo "Data pull successful."
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
                echo "${ENV_FILE}"
                exit 200
        fi
}

# Main logic starts here.
if [[ lock_execution -eq 0 ]]; then
        echo "Lock ${LOCK_FILE} was not successful."
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