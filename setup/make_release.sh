#!/bin/bash
set -e

if [ ! -f pkgutils.py ]; then
    echo "Must be called from the root folder of the source"
    exit 1
fi

echo ""
echo " Building Dependencies"
echo "================================================================================"
echo ""
pdm run pkgutils.py build-assets
pdm run pkgutils.py icons optional

echo ""
echo " Building Linux Packages"
echo "================================================================================"
echo ""
pdm run pkgutils.py build-deb --sign
pdm run pkgutils.py build-ubuntu --sign
