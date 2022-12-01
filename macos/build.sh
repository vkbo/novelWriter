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

echo "Building in: $BUILD_DIR"

OLD_CWD="$(pwd)"

VERSION="$(awk '/^__version__/{print substr($NF,2,length($NF)-2)}' $SCRIPT_DIR/../novelwriter/__init__.py)"


pushd "$BUILD_DIR"/ || exit 1

echo "Downloading Miniconda ..."
# install Miniconda, a self-contained Python distribution
curl -LO https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh -b -p ~/miniconda -f
rm Miniconda3-latest-MacOSX-x86_64.sh 
export PATH="$HOME/miniconda/bin:$PATH"

echo "Creating conda env ..."
# create conda env
conda create -n novelWriter -c conda-forge python=3.10 --yes
source activate novelWriter

echo "installing dictionaries ..."
conda install -c conda-forge enchant hunspell-en --yes

echo "installing python deps ..."
# install dependencies
pip install -r "$SCRIPT_DIR/../requirements.txt"

# leave conda env
conda deactivate

echo "Building app bundle ..."
# create .app Framework
mkdir -p novelWriter.app/Contents/
mkdir novelWriter.app/Contents/MacOS novelWriter.app/Contents/Resources novelWriter.app/Contents/Resources/novelWriter
cp $SCRIPT_DIR/../macos/Info.plist novelWriter.app/Contents/Info.plist

echo "Copying miniconda env to bundle ..."
# copy Miniconda env
cp -R ~/miniconda/envs/novelWriter/* novelWriter.app/Contents/Resources/

echo "Copying novelWriter to bundle ..."
# copy novelWriter

FILES_COPY=(
    "CHANGELOG.md" "MANIFEST.in" "CREDITS.md" "LICENSE.md"
    "CONTRIBUTING.md" "CODE_OF_CONDUCT.md" "i18n" "novelwriter"
    "novelWriter.py"
)

for file in "${FILES_COPY[@]}"; do
    echo "Copying $SCRIPT_DIR/../$file ..."
    cp -R $SCRIPT_DIR/../$file novelWriter.app/Contents/Resources/novelWriter/
done

cp $SCRIPT_DIR/../macos/novelwriter.icns novelWriter.app/Contents/Resources/
#cp -R $SCRIPT_DIR/../* novelWriter.app/Contents/Resources/novelWriter/


# create entry script
cat > novelWriter.app/Contents/MacOS/novelWriter <<\EOF
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
$DIR/../Resources/bin/python -sE $DIR/../Resources/novelWriter/novelWriter.py $@
EOF

# make executable
chmod a+x novelWriter.app/Contents/MacOS/novelWriter

sudo codesign --sign - --deep --force --entitlements "$SCRIPT_DIR/../macos/App.entitlements" --options runtime "novelWriter.app/Contents/MacOS/novelWriter"

# remove bloat
pushd novelWriter.app/Contents/Resources || exit 1

echo "Cleaning unused files from bundle ..."
# cleanup commands HERE
find . -type d -iname '__pycache__' -print0 | xargs -0 rm -r

rm -rf pkgs
rm -rf cmake
rm -rf share/{gtk-,}doc

#remove web engine
rm lib/python3.*/site-packages/PyQt5/QtWebEngine* || true
rm -r lib/python3.*/site-packages/PyQt5/Qt/translations/qtwebengine* || true
rm lib/python3.*/site-packages/PyQt5/Qt/resources/qtwebengine* || true
rm -r lib/python3.*/site-packages/PyQt5/Qt/qml/QtWebEngine* || true
rm -r lib/python3.*/site-packages/PyQt5/Qt/plugins/webview/libqtwebview* || true
rm lib/python3.*/site-packages/PyQt5/Qt/libexec/QtWebEngineProcess* || true
rm lib/python3.*/site-packages/PyQt5/Qt/lib/libQt5WebEngine* || true

popd || exit 1
popd || exit 1

echo "Packageing App ..."



# generate .dmg

brew install create-dmg
# "--skip-jenkins" is a temporary workaround for https://github.com/create-dmg/create-dmg/issues/72
create-dmg --volname "novelWriter $VERSION" --volicon $SCRIPT_DIR/../macos/novelwriter.icns \
    --window-pos 200 120 --window-size 800 400 --icon-size 100 --icon novelWriter.app 200 190 --hide-extension novelWriter.app \
    --app-drop-link 600 185 novelWriter-"${VERSION}".dmg "$BUILD_DIR"/

pushd $BUILD_DIR || exit 1
zip -qr novelWriter.app.zip  novelWriter.app
popd || exit 1

mv $BUILD_DIR/novelWriter.app.zip novelWriter.app.zip