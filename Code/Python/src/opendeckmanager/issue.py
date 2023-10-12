import tkinter
import threading
from pynput import keyboard


class KeyRecorder:
    def __init__(self) -> None:
        self.listener = None
        self.callback = None
        self.macro = []

    def record(self, seconds, callback):
        self.callback = callback
        self.macro.clear()

        def on_press(key):
            self.macro.append(('press', key))
            return True

        def on_release(key):
            self.macro.append(('release', key))
            return True

        def end_recording():
            self.listener.stop()
            self.callback(self.macro)

        self.listener = keyboard.Listener(
            on_press=on_press, on_release=on_release)
        self.listener.start()

        timer = threading.Timer(seconds, end_recording)
        timer.start()

key_recorder = KeyRecorder()


def record():
    def handle_recording(keys):
        print(f"Callback called: {keys}")

    key_recorder.record(5, handle_recording)


app = tkinter.Tk()

button = tkinter.Button(command=record, text="Record")
button.pack(pady=20)

app.mainloop()

