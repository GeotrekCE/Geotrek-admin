#!/bin/bash

DATABASE=$1 # "medium" or "big"
SESSION_ID=$2
MEASURES_DIR=./time_measures

NB_MEASURES=15
STEPS_MEDIUM_DB='{"steps":[{"lat":48.57432140000001,"lng":-0.767637499999998},{"lat":48.63950999243303,"lng":0.2604644963783054}]}'
STEPS_BIG_DB='{"steps":[{"lat":48.63950999243303,"lng":0.2604644963783054}]}'

launch_scenario() {
# $1 (boolean): if true, keep the backend cache before each spec run

    # Reset the time measure files
    if [ -d "$MEASURES_DIR" ]; then
        rm -f "$MEASURES_DIR"/time_measures_*
    else
        mkdir "$MEASURES_DIR"
    fi

    for i in $(seq 1 $NB_MEASURES)
    do
        if ! $1; then
            # Empty the backend cache
            curl 'http://geotrek.local:8000/admin/clearcache/' -X POST -H "Cookie: csrftoken=jJPzy1w4p7KNspD9QG1Y2xOqG8Oczf2l; sessionid=$SESSION_ID" --data-raw 'csrfmiddlewaretoken=VihAxtR8JyN10VzyXyyEAUSiwWIbVnPG4RWZVkd2YvnEia2xD4psshwy2UmdksHR&cache_name=fat'
        fi

        if [[ "$DATABASE" == "medium" ]]; then
            STEPS="$STEPS_MEDIUM_DB"
        else
            STEPS="$STEPS_BIG_DB"
        fi
        # Send a request to take the time measures
        curl 'http://geotrek.local:8000/api/path/drf/paths/route-geometry' -X POST \
             -H 'X-CSRFToken: DKUegVuaV01Lsb2s4ORLTx6dqG7CWiFP' \
             -H 'Content-Type: application/json; charset=UTF-8' \
             -H "Cookie: csrftoken=DKUegVuaV01Lsb2s4ORLTx6dqG7CWiFP; sessionid=$SESSION_ID" \
             --data-raw "$STEPS" \
             -s -o /dev/null
        echo '' >> "$MEASURES_DIR"/time_measures_py.txt
    done

    # Compute and display the average times
    echo "Branch:" $(git rev-parse --abbrev-ref HEAD) >> "$MEASURES_DIR"/time_averages.txt
    echo "Database:" $DATABASE >> "$MEASURES_DIR"/time_averages.txt
    echo "Backend cache:" $1 >> "$MEASURES_DIR"/time_averages.txt
    echo "Number of runs:" $NB_MEASURES >> "$MEASURES_DIR"/time_averages.txt
    python3 ./time_averages.py >> "$MEASURES_DIR"/time_averages.txt
    echo "" >> "$MEASURES_DIR"/time_averages.txt
}

# Reset the time averages files
if [ -d "$MEASURES_DIR" ]; then
        rm -f "$MEASURES_DIR"/time_averages.txt
    else
        mkdir "$MEASURES_DIR"
    fi
launch_scenario false
launch_scenario true