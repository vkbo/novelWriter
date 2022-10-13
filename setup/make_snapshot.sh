#!/bin/bash
set -e

if [ ! -f setup.py ]; then
    echo "Must be called from the root folder of the source"
    exit 1
fi

echo ""
echo " Building Dependencies"
echo "================================================================================"
echo ""
python3 setup.py clean-assets
python3 setup.py qtlrelease manual sample

echo ""
echo " Building Linux Snapshots"
echo "================================================================================"
echo ""
python3 setup.py build-ubuntu --sign --snapshot
