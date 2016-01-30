#!/bin/bash

echo "** hansardku: spinning up"

command="$1"

if [ x"$command" = x"uwsgi" ]; then
    cd /app &&
        uwsgi_python34 -s :8889 -w hansardku.wsgiku:app --master -p 16 --lazy
    while true; do
        echo "** uwsgi has quit: sleep 30 **"
        sleep 30
    done
fi

echo "executing: $*"
exec $*
