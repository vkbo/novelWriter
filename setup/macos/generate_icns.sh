#! /usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

function generate_linux () {
    echo "Generating on Linux ..."
    if ! command -v png2icns &> /dev/null
    then
        echo "png2icns cound not be found, it is required. Please install a package like icnsutils or libicns."
        exit
    fi

    if ! command -v convert $> /dev/null
    then
        echo "convert could not be found, it is required. please install a imagemagick package."
        exit
    fi

    mkdir -p $SCRIPT_DIR/icons

    sizes=( 16 32 64 128 256 )
    for base in "${sizes[@]}"; do
        let basex2=${base}*2
        size="${base}x${base}"
        echo "Copying files for $size"
        double=${basex2}x${basex2}
        cp $SCRIPT_DIR/../data/hicolor/${size}/apps/novelwriter.png $SCRIPT_DIR/icons/icon_${size}.png
        echo "Resizing ${size}@2x to $double from $size"
        convert $SCRIPT_DIR/icons/icon_${size}.png -resize $double $SCRIPT_DIR/icons/icon_${size}@2x.png    
    done

    png2icns $SCRIPT_DIR/novelwriter.icns $SCRIPT_DIR/icons/icon_*.png

    rm -r $SCRIPT_DIR/icons

    echo "Done"
}

function generate_macos () {
    echo "Generating on MacOs ..."
    mkdir -p $SCRIPT_DIR/icons

    echo "Building Iconset ..."
    sizes=( 16 32 64 128 256 )
    for base in "${sizes[@]}"; do
        let basex2=${base}*2
        size="${base}x${base}"
        echo "Copying files for $size"
        double=${basex2}x${basex2}
        cp $SCRIPT_DIR/../data/hicolor/${size}/apps/novelwriter.png $SCRIPT_DIR/icons/icon_${size}.png
        cp $SCRIPT_DIR/../data/hicolor/${size}/apps/novelwriter.png $SCRIPT_DIR/icons/icon_${size}@2x.png
        echo "Resizing ${size}@2x to $double from $size"
        sips -Z $basex2 $SCRIPT_DIR/icons/icon_${size}@2x.png    
    done

    rm -rf $SCRIPT_DIR/novelwriter.iconset
    mv $SCRIPT_DIR/icons $SCRIPT_DIR/novelwriter.iconset

    echo "Generating icns ..."
    iconutil -c icns $SCRIPT_DIR/novelwriter.iconset

    echo "Done"
}

unameOut="$(uname -s)"
case "$unameOut" in
    Linux*)    generate_linux;;
    Darwin*)    generate_macos;;
    *)    echo "Unsupported OS"
esac
