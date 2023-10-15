import tkinter
import threading
from pynput import keyboard


class KeyRecorder:
    def __init__(self) -> None:
        self.callback = None
        self.macro = []

        def on_press(key):
            self.macro.append(("press", key))
            return True

        self.on_press = on_press

        def on_release(key):
            self.macro.append(("release", key))
            return True

        self.on_release = on_release

    def record(self, seconds):
        self.macro.clear()
        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.listener.start()

        def end_recording():
            global state
            self.listener.stop()
            self.callback(self.macro)
            self.macro.clear()

        global state
        timer = threading.Timer(seconds, end_recording)
        timer.start()


key_recorder = KeyRecorder()
kb_wait_event = threading.Event()


def record():
    def handle_recording(keys):
        print(f"Callback called: {keys}")

    key_recorder.callback = handle_recording
    kb_wait_event.set()


def kb_wait():
    global key_recorder
    global kb_wait_event
    while True:
        if kb_wait_event.wait():
            key_recorder.record(5)
            kb_wait_event.clear()


kb_wait_thread = threading.Thread(target=kb_wait).start()

app = tkinter.Tk()

button = tkinter.Button(command=record, text="Record")
button.pack(pady=20)

app.mainloop()
