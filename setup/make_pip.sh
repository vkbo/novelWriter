#!/bin/bash
set -e

ENVPATH=/tmp/nwBuild

if [ ! -f pkgutils.py ]; then
    echo "Must be called from the root folder of the source"
    exit 1
fi

echo ""
echo " Create Python Env"
echo "================================================================================"
echo ""

if [ ! -d $ENVPATH ]; then
    python3 -m venv $ENVPATH
fi
source $ENVPATH/bin/activate
pip3 install -U build twine -r requirements.txt -r docs/requirements.txt

echo ""
echo " Building Dependencies"
echo "================================================================================"
echo ""
python3 pkgutils.py build-assets

echo ""
echo " Building Packages"
echo "================================================================================"
echo ""
python3 -m build
mkdir -pv dist_upload
cp -v dist/novelwriter-*.whl dist_upload/
cd dist_upload
FILE=$(ls -t | head -1)
shasum -a 256 $FILE | tee $FILE.sha256
cd ..

echo ""
echo " Checking Packages"
echo "================================================================================"
echo ""
twine check dist/*
deactivate

echo ""
echo " Done!"
echo "================================================================================"
echo ""
echo " To upload packages to PyPi, run:"
echo " python3 -m twine upload dist/*"
echo ""
