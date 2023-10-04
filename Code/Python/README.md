# Open Deck GUI

## macOS support

The purpose of this fork is to improve macOS support for Open Deck.

To install dependencies, run `pip3 install -e '.[dev]'` in `Code/Python/`.

macOS requires users to give explicit permission to an app to generate keystrokes or record them. In order to limit the scope of the permission that is granted, we want to package the Open Deck GUI as a macOS app instead of running it as a python script. 

To do this, we are using PyInstaller from <https://pyinstaller.org/>. There are other tools, like py2app, but this one was the first that worked correctly with the least effort. 