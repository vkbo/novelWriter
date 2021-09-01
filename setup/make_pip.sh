#!/bin/bash
set -e

if [ ! -f setup.py ]; then
    echo "Must be called from the root folder of the source"
    exit 1
fi

echo ""
echo " Building Packages"
echo "================================================================================"
echo ""
python3 setup.py sdist bdist_wheel

echo ""
echo " Checking Packages"
echo "================================================================================"
echo ""
twine check dist/*

echo ""
echo " Done!"
echo "================================================================================"
echo ""
echo " To upload packages to PyPi, run:"
echo " twine upload Source/dist/*"
echo ""
