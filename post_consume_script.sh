#!/usr/bin/env bash

RUN_DIR=$( dirname -- "$( readlink -f -- "$0"; )"; )
export RUN_DIR=$RUN_DIR
source $RUN_DIR/venv/bin/activate
$RUN_DIR/change_title.py