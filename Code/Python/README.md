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
* Image upload

Work in progress:
* Moving configuration and persistence to a new module. 
  * Need to add back a default list of macros. 
  * Need to add the rest of the app settings, not must macros

These operations are not implemented for macOS yet:
* Macro key recording: pynput Listener is crashing
* "Menu Change Opens Computer App"/"Macro Button Opens Computer App": need to find a way to activate the window, probably using osascript

This work needs to be done:
* Verify the code on Windows 
* Profile to see if any optimization is necessary 
* Replace pickle with a more secure serialization mechanism

### Additional information

You must plug the Open Deck directly into the Mac, not a USB hub. You'll be prompted to allow the device to connect. After it has been authorized, it will work from a USB hub.

