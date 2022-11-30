#! /bin/bash

# use RAM disk if possible
if [ -d /dev/shm ]; then
    TEMP_BASE=/dev/shm
else
    TEMP_BASE=/tmp
fi

BUILD_DIR=$(mktemp -d "$TEMP_BASE/novelWriter-build-XXXXXX")

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cleanup () {
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
    fi
}

trap cleanup EXIT

OLD_CWD="$(pwd)"

VERSION="$(awk '/^__version__/{print substr($NF,2,length($NF)-2)}' $SCRIPT_DIR/../novelwriter/__init__.py)"


pushd "$BUILD_DIR"/ || exit 1

# install Miniconda, a self-contained Python distribution
wget https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh -b -p ~/miniconda -f
rm Miniconda3-latest-MacOSX-x86_64.sh 
export PATH="$HOME/miniconda/bin:$PATH"

# create conda env
conda create -n novelWriter python --yes
source activate novelWriter

# install dependencies
pip install -r "$SCRIPT_DIR/../requirements.txt"

# leave conda env
source deactivate

# create .app Framework
mkdir -p novelWriter.app/Contents/
mkdir novelWriter.app/Contents/MacOS novelWriter.app/Contents/Resources novelWriter.app/Contents/Resources/novelWriter
mv $SCRIPT_DIR/../macos/Info.plist novelWriter.app/Contents/Info.plist

# copy Miniconda env
cp -R ~/miniconda/envs/novelWriter/* novelWriter.app/Contents/Resources/

# copy Pext
cp -R $SCRIPT_DIR/../* novelWriter.app/Contents/Resources/novelWriter/


# create entry script
cat > novelWriter.app/Contents/MacOS/novelWriter <<\EOF
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
$DIR/../Resources/bin/python -sE $DIR/../Resources/novelWriter/novelwriter $@
EOF

# make executable
chmod a+x novelWriter.app/Contents/MacOS/novelWriter

# remove bloat
pushd novelWriter.app/Contents/Resources || exit 1

# cleanup commands HERE
find . -type d -iname '__pycache__' -print0 | xargs -0 rm -r

#remove web engine
rm lib/python3.7/site-packages/PyQt5/QtWebEngine* || true
rm -r lib/python3.7/site-packages/PyQt5/Qt/translations/qtwebengine* || true
rm lib/python3.7/site-packages/PyQt5/Qt/resources/qtwebengine* || true
rm -r lib/python3.7/site-packages/PyQt5/Qt/qml/QtWebEngine* || true
rm -r lib/python3.7/site-packages/PyQt5/Qt/plugins/webview/libqtwebview* || true
rm lib/python3.7/site-packages/PyQt5/Qt/libexec/QtWebEngineProcess* || true
rm lib/python3.7/site-packages/PyQt5/Qt/lib/libQt5WebEngine* || true

popd || exit 1
popd || exit 1


# generate .dmg

brew install create-dmg
# "--skip-jenkins" is a temporary workaround for https://github.com/create-dmg/create-dmg/issues/72
create-dmg --skip-jenkins --volname "novelWriter $VERSION" --volicon $SCRIPT_DIR/../macos/novelwriter.icns \
    --window-pos 200 120 --window-size 800 400 --icon-size 100 --icon novelWriter.app 200 190 --hide-extension novelWriter.app \
    --app-drop-link 600 185 novelWriter-"${VERSION}".dmg "$BUILD_DIR"/
