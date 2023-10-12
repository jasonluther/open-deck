"""
Record keystrokes to be used as a macro
"""

import threading
from pynput import keyboard


class KeyRecorder:
    def __init__(self, logger=None) -> None:
        self.listener = None
        self.callback = None
        self.logger = logger
        self.macro = []

    def log(self, msg, *args, **kwargs):
        if self.logger:
            self.logger.debug(msg, *args, **kwargs)

    def record(self, seconds, callback):
        self.callback = callback
        self.macro.clear()
        self.log("Recording")

        def on_press(key):
            self.macro.append(('press', key))
            self.log(f"press {key}")
            return True

        def on_release(key):
            self.macro.append(('release', key))
            self.log(f"release {key}")
            return True

        def end_recording():
            self.log("End recording")
            self.listener.stop()
            self.callback(self.macro)

        self.listener = keyboard.Listener(
            on_press=on_press, on_release=on_release)
        self.listener.start()

        self.log("Start timer")
        timer = threading.Timer(seconds, end_recording)
        timer.start()
        self.log("Done")


def example():
    import logging as log
    import time
    log.basicConfig(encoding='utf-8', level=log.DEBUG)

    k = KeyRecorder(log)

    def callback(macro):
        log.info("Callback called")
        log.info(f"Macro: {macro}")
    sleep_seconds = 5
    log.info("Example: k.record()")
    k.record(seconds=sleep_seconds, callback=callback)
    log.info("Example: sleep")
    time.sleep(sleep_seconds+1)
    log.info("Example: done")
    log.info(f"k.macro = {k.macro}")


if __name__ == "__main__":
    example()
