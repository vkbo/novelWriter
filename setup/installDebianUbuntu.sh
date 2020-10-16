#!/bin/bash

cd ..

EXEC=$(pwd)/novelWriter.py
EXEC=$(echo $EXEC | sed 's_/_\\/_g')

sed "s/%%exec%%/$EXEC/g" setup/novelwriter.desktop > /usr/share/applications/novelwriter.desktop

if [ ! -d /usr/share/icons/hicolor/24x24/apps ]; then
    mkdir -pv /usr/share/icons/hicolor/24x24/apps
fi
if [ ! -d /usr/share/icons/hicolor/48x48/apps ]; then
    mkdir -pv /usr/share/icons/hicolor/48x48/apps
fi
if [ ! -d /usr/share/icons/hicolor/96x96/apps ]; then
    mkdir -pv /usr/share/icons/hicolor/96x96/apps
fi
if [ ! -d /usr/share/icons/hicolor/256x256/apps ]; then
    mkdir -pv /usr/share/icons/hicolor/256x256/apps
fi
if [ ! -d /usr/share/icons/hicolor/512x512/apps ]; then
    mkdir -pv /usr/share/icons/hicolor/512x512/apps
fi
if [ ! -d /usr/share/icons/hicolor/scalable/apps ]; then
    mkdir -pv /usr/share/icons/hicolor/scalable/apps
fi
if [ ! -d /usr/share/icons/hicolor/scalable/mimetypes ]; then
    mkdir -pv /usr/share/icons/hicolor/scalable/mimetypes
fi

cp -v setup/icons/24x24/novelwriter.png     /usr/share/icons/hicolor/24x24/apps/
cp -v setup/icons/48x48/novelwriter.png     /usr/share/icons/hicolor/48x48/apps/
cp -v setup/icons/96x96/novelwriter.png     /usr/share/icons/hicolor/96x96/apps/
cp -v setup/icons/256x256/novelwriter.png   /usr/share/icons/hicolor/256x256/apps/
cp -v setup/icons/512x512/novelwriter.png   /usr/share/icons/hicolor/512x512/apps/
cp -v setup/icons/novelwriter.svg           /usr/share/icons/hicolor/scalable/apps/
cp -v setup/icons/x-novelwriter-project.svg /usr/share/icons/hicolor/scalable/mimetypes/application-x-novelwriter-project.svg
cp -v setup/mime/x-novelwriter-project.xml  /usr/share/mime/packages/

update-mime-database /usr/share/mime/
update-icon-caches /usr/share/icons/*
