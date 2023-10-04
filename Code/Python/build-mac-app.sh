#!/bin/sh

./clean.sh
 pyinstaller --onefile --windowed --name "Open Deck Manager" src/opendeckmanager/__main__.py
 open dist/