#!/bin/bash
set -e

if [ ! -f setup.py ]; then
    echo "Must be called from the root folder of the source"
    exit 1
fi

rm -rfv dist_upload
python3 setup.py build-clean
