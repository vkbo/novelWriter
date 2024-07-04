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
echo " Building Packages"
echo "================================================================================"
echo ""
python3 -m build
mkdir -pv dist_upload
cp -v dist/novelWriter-*.whl dist_upload/
cd dist_upload
FILE=$(ls -t | head -1)
shasum -a 256 $FILE | tee $FILE.sha256
cd ..

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
echo " twine upload dist/*"
echo ""
