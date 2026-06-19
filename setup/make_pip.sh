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
uv run pkgutils.py build-assets
uv run pkgutils.py icons optional

echo ""
echo " Building Packages"
echo "================================================================================"
echo ""
uv build
mkdir -pv dist_upload
cp -v dist/novelwriter-*.whl dist_upload/
cd dist_upload
FILE=$(ls -t | head -1)
shasum -a 256 $FILE | tee $FILE.sha256
cd ..

echo ""
echo " Done!"
echo "================================================================================"
echo ""
echo " To upload packages to PyPi, run:"
echo " python3 -m twine upload dist/*"
echo ""
