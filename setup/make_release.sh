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
python3 pkgutils.py clean-assets
python3 pkgutils.py qtlrelease manual sample

echo ""
echo " Building Minimal Packages"
echo "================================================================================"
echo ""
python3 pkgutils.py minimal-zip --target-win
python3 pkgutils.py minimal-zip --target-linux
python3 pkgutils.py minimal-zip --target-darwin

echo ""
echo " Building Linux Packages"
echo "================================================================================"
echo ""
python3 pkgutils.py build-deb --sign
python3 pkgutils.py build-ubuntu --sign --first
