#!/bin/bash
set -e

if [ ! -f setup.py ]; then
    echo "Must be called from the root folder of the source"
    exit 1
fi

python3 setup.py clean
