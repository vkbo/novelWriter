#! /usr/bin/env bash

if ! command -v png2icns &> /dev/null
then
    echo "png2icns cound not be found, it is required. Please install a package like icnsutils or libicns."
    exit
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

mkdir -p $SCRIPT_DIR/icons

for size in 16x16 32x32 48x48 128x128 256x256; do
    cp $SCRIPT_DIR/../setup/data/hicolor/$size/apps/novelwriter.png $SCRIPT_DIR/icons/icon_${size}px.png
done

png2icns $SCRIPT_DIR/novelwriter.icns $SCRIPT_DIR/icons/icon_*px.png

rm -r $SCRIPT_DIR/icons