# Open Deck GUI

## macOS support

The purpose of this fork is to improve macOS support for Open Deck.

To install dependencies, run `pip3 install -e '.[dev]'` in `Code/Python/`.

macOS requires users to give explicit permission to an app to generate keystrokes or record them. In order to limit the scope of the permission that is granted, we want to package the Open Deck GUI as a macOS app instead of running it as a python script. 

To do this, we are using PyInstaller from <https://pyinstaller.org/>. There are other tools, like py2app, but this one was the first that worked correctly with the least effort. 

### Progress

These basic operations of Open Deck appear to work:
* Serial port selection
* Manual macro configuration
* Application detection and automatic menu selection
* Macro execution

These operations are not tested yet:
* Image upload

These operations are not implemented for macOS yet:
* Macro key recording
* "Menu Change Opens Computer App"/"Macro Button Opens Computer App"

The operation of the code on Windows has not been done. 

### Additional information

You must plug the Open Deck directly into the Mac, not a USB hub. You'll be prompted to allow the device to connect. After it has been authorized, it will work from a USB hub. (DOUBLE CHECK)
