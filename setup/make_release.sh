#!/bin/bash
set -e

if [ ! -f setup.py ]; then
    echo "Must be called from the root folder of the source"
    exit 1
fi

echo ""
echo " Building Minimal Packages"
echo "================================================================================"
echo ""
python3 setup.py minimal-zip --target-win
python3 setup.py minimal-zip --target-linux
python3 setup.py minimal-zip --target-darwin

echo ""
echo " Building Linux Packages"
echo "================================================================================"
echo ""
python3 setup.py build-deb --sign
python3 setup.py build-ubuntu --sign --first
