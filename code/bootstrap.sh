#!/bin/bash -x 

VENV_PATH="$1"
if [ x"$VENV_PATH" = x ]; then
    echo "usage: $0 <venv_path>"
    exit 1;
fi

venv()
{
    #
    # Set up VirtualEnv
    #

    if [ -e "$VENV_PATH" ]; then 
        echo "cleaning up: $VENV_PATH"
        rm -rf "$VENV_PATH"
    fi
    # include system so we can pull in mapscript
    virtualenv --system-site-packages -p /usr/bin/python3.3 "$VENV_PATH"
    "$VENV_PATH"/bin/pip install simplejson markdown flask
    "$VENV_PATH"/bin/pip install git+https://github.com/mitsuhiko/flask-sqlalchemy
}

venv
