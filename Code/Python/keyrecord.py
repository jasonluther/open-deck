#!/usr/bin/env python3
from pynput.keyboard import Key, Listener
import time

pressed_keys = []

def record_keystrokes():

    def on_press(key):
        print(f"key press: {key}")
        pressed_keys.append(("press", key))

    def on_release(key):
        print(f"key release: {key}")
        pressed_keys.append(("release", key))


    print("Starting")
    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()
    return listener

def finish_keystrokes(listener):
    listener.stop()
    print(pressed_keys)

l = record_keystrokes()
time.sleep(5)
finish_keystrokes(l)