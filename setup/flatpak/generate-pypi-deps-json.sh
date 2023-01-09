#! /bin/sh
# uses https://github.com/flatpak/flatpak-builder-tools/blob/master/pip/flatpak-pip-generator

cp ../requirements.txt .
sed -e '/pyqt5/s/^/#/g' -i requirements.txt
curl -LO https://github.com/flatpak/flatpak-builder-tools/raw/master/pip/flatpak-pip-generator
python3 flatpak-pip-generator \
    --requirements-file=requirements.txt \
    --runtime=com.riverbankcomputing.PyQt.BaseApp//5.15-22.08 \
    -o pypi-deps
rm requirements.txt
rm flatpak-pip-generator