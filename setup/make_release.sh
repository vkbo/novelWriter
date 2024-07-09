#!/bin/bash
set -e

ENVPATH=/tmp/nwBuild

if [ ! -f pkgutils.py ]; then
    echo "Must be called from the root folder of the source"
    exit 1
fi

echo ""
echo " Building Dependencies"
echo "================================================================================"
echo ""
if [ ! -d $ENVPATH ]; then
    python3 -m venv $ENVPATH
fi
source $ENVPATH/bin/activate
pip3 install -r docs/source/requirements.txt
python3 pkgutils.py build-assets
deactivate

echo ""
echo " Building Linux Packages"
echo "================================================================================"
echo ""
python3 pkgutils.py build-deb --sign
python3 pkgutils.py build-ubuntu --sign --first
