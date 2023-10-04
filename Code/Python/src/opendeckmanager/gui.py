from imaplib import Commands
from pynput.keyboard import Key, Controller
from threading import *
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter.colorchooser import askcolor
import customtkinter
import cv2
import logging
import math
import numpy as np
import pickle
import pygetwindow as gw  # for window switching (windows only)
import serial
import serial.tools.list_ports
import sys
import time
import tkinter

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

keyboard = Controller()

saveDataFilename = 'data.pk'  # pickle file to save the data

ser = serial.Serial()

COMports = []

prevPort = "Select"

# Defaults, New values are stored in data.pk
switchStates = ["off", "on", "on", "on"]

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

BUTTON_OPTIONS = ["Menu 1", "Menu 2", "Menu 3", "Menu 4", "Menu 5", "Menu 6", "Menu 7", "Menu 8", "Menu 9",
                  "Menu 10", "Menu 11", "Menu 12", "Menu 13", "Menu 14", "Menu 15", "Menu 16", "Menu 17", "Menu 18"]

HOME_OPTIONS = ["App 1", "App 2", "App 3", "App 4", "App 5", "App 6"]

OPTIONS = ["Home 1", "Home 2", "Home 3", "Home 4", "Home 5", "Home 6", "Menu 1", "Menu 2", "Menu 3", "Menu 4", "Menu 5", "Menu 6",
           "Menu 7", "Menu 8", "Menu 9", "Menu 10", "Menu 11", "Menu 12", "Menu 13", "Menu 14", "Menu 15", "Menu 16", "Menu 17", "Menu 18"]

# remove this in future and just edit name (current way is dumb, just for testing)
name_dict = {"Home 1": b'home_1\n', "Home 2": b'home_2\n', "Home 3": b'home_3\n', "Home 4": b'home_4\n', "Home 5": b'home_5\n', "Home 6": b'home_6\n', "Menu 1": b'menu_1\n', "Menu 2": b'menu_2\n', "Menu 3": b'menu_3\n', "Menu 4": b'menu_4\n', "Menu 5": b'menu_5\n', "Menu 6": b'menu_6\n',
             "Menu 7": b'menu_7\n', "Menu 8": b'menu_8\n', "Menu 9": b'menu_9\n', "Menu 10": b'menu_10\n', "Menu 11": b'menu_11\n', "Menu 12": b'menu_12\n', "Menu 13": b'menu_13\n', "Menu 14": b'menu_14\n', "Menu 15": b'menu_15\n', "Menu 16": b'menu_16\n', "Menu 17": b'menu_17\n', "Menu 18": b'menu_18\n'}


# Defaults, New values are stored in data.pk
key_dict = {
    1: [['alt+left'], "Back"],
    2: [['alt+right'], "Forwards"],
    3: [['ctrl+r'], "Reload"],
    4: [['previous track'], "Prev Track"],
    5: [['next track'], "Next Track"],
    6: [['play/pause media'], "pause"],
    7: [['ctrl+s', 'ctrl+alt+n'], "Run"],
    8: [['ctrl+alt+m'], "Stop"],
    9: [['ctrl+s'], "Save"],
    10: [['ctrl+shift+esc'], "Task Manager"],
    11: [['alt+tab'], "alt tab"],
    12: [['windows+shift+s'], "Snipping Tool"],
    13: [['ctrl+r'], "Mid Rect"],
    14: [['ctrl+a'], "Arc"],
    15: [['ctrl+f'], "Chamfer"],
    16: [['ctrl+r'], "Verify"],
    17: [['ctrl+s', 'ctrl+u'], "Upload"],
    18: [['ctrl+shift+m'], "Serial Monitor"],
}

# Defaults, New values are stored in data.pk
app_dict = {
    1: "Chrome",
    2: "",
    3: "visual studio code",
    4: "",
    5: "fusion",
    6: "arduino"
}

app = customtkinter.CTk()
app.geometry("800x900")
app.title("Macro Keyboard Configure")


def updatePorts():
    """
    Constantly refresh ports
    Will change selection if current port no longer available as well as auto
    detect if no current port is currently selected
    """
    global ser
    global COMports
    global prevPort
    ports = serial.tools.list_ports.comports()
    lastPorts = COMports
    COMports = ["Select"]
    for port, desc, hwid in sorted(ports):
        COMports.append(port+": "+desc)
    if (lastPorts != COMports):
        logging.info("Port change detected")
        lastPorts = COMports
        portSelect.configure(values=COMports)
        # portSelect.values=COMports  #not working use .configure instead

        if (portSelect.get() not in COMports):  # issue here???????
            logging.debug("Old port no longer detected, un-selecting")
            portSelect.set("Select")
        if (portSelect.get() == "Select" and connectSwitch.get() == "on"):
            detectPort(ports)

    if (ser.isOpen() == False or prevPort != portSelect.get()):  # OR USER CHANGED BAUD RATE
        ser.close()  # close current port before trying new one
        prevPort = portSelect.get()
        try:
            # check to see if already open first?????
            # let user choose in future
            ser = serial.Serial(portSelect.get(), baudSelect.get())
            ser.timeout = 0.5
            connectLabel.configure(text="Connected", text_color="green")
        except:
            connectLabel.configure(text="Not Connected", text_color="red")


def detectPort(ports):
    for port, desc, hwid in sorted(ports):
        if ("USB-SERIAL CH340" in desc or "USB Serial" in desc):
            logging.info(f"Auto-detect port: {port}")
            portSelect.set(port)


##################################
#       get data from pickle
##################################
try:
    with open(saveDataFilename, 'rb') as fi:
        key_dict, app_dict, switchStates = pickle.load(fi)
except:
    logging.warning("Could not import saved data from pickle file")


def pickleData():
    logging.debug("Saving data to pickle file")
    with open(saveDataFilename, 'wb') as fi:
        pickle.dump([key_dict, app_dict, switchStates], fi)

##################################
#     GUI callbacks
##################################


def macro_update():
    """
    Handle Macro Setup "Update" button
    """
    buttonNum = int(macroCombobox.get()[5:])
    key_dict[buttonNum][1] = nameEntry.get()
    entry = macroEntry.get()
    commands = entry.split(",")
    finalCommands = []
    for command in commands:
        command.strip()
        # command.replace(" ", "") #remove any white spaces (actually still need this for next track)
        if (command != ""):
            finalCommands.append(command)
    key_dict[buttonNum][0] = finalCommands
    logging.debug(f"Button click: {macroCombobox.get()}")
    pickleData()


def app_update():
    """
    Handle Application Setup "App Name" update
    """
    appNum = int(appCombobox.get()[4:])
    app_dict[appNum] = appEntry.get()  # update app name in dict
    logging.debug(f"Button click: {appCombobox.get()}")
    pickleData()


def macroCombobox_callback(choice):
    """
    Handle Macro Setup "Button Number" dropdown change
    """
    logging.debug(f"combobox dropdown clicked: {choice}")
    num = int(choice[5:])
    logging.debug(f"combobox dropdown num: {num}")
    macroEntry.delete(0, 'end')
    if (len(key_dict[num][0]) > 1):
        count = 0
        for item in key_dict[num][0]:
            count += 1
            item.replace("{", "")  # remove any weird brackets added?
            item.replace("}", "")  # remove any weird brackets added?
            macroEntry.insert('end', item)
            if (count < len(key_dict[num][0])):
                macroEntry.insert('end', ', ')
    else:
        macroEntry.insert(0, key_dict[num][0])
    nameEntry.delete(0, 'end')
    nameEntry.insert(0, key_dict[num][1])
    appCombobox.set("App "+str(math.ceil(num/3)))

# app dropdown changed


def appCombobox_Callback(choice):
    """
    Handle Application Setup "App Number" dropdown change
    """
    logging.debug(f"combobox dropdown clicked: {choice}")
    num = int(choice[4:])
    logging.debug(f"combobox dropdown num: {num}")
    butNumLabel.configure(
        text=("Buttons " + str(num*3-2) + ", " + str(num*3-1) + ", " + str(num*3)))
    appEntry.delete(0, 'end')
    appEntry.insert(0, app_dict[num])


def macro_record():
    """
    Handle Macro Setup "Record Keys" button
    XXX This is broken right now due to the change from 'keyboard' to 'pynput'
    """
    logging.info("Recording Keys")  # change button colour while recording
    recButton.configure(state=tkinter.DISABLED)
    keyboard.start_recording()
    time.sleep(5)
    events = keyboard.stop_recording()
    count = 0  # add 1 for every down if down = up then add comma
    combo = ""
    lastEvent = None
    for event in events:
        if (event != lastEvent):
            if (event.event_type == "down"):
                combo += event.name + "+"
            elif (event.event_type == "up"):
                combo = combo[:len(combo)-1]  # remove + for, if end of a combo
                combo += ","
        lastEvent = event
    # combo.strip()
    # remove last comma and space (not sure how it removes all?)
    combo = combo[:len(combo)-1]
    logging.debug(f"{combo}")
    recButton.configure(state=tkinter.NORMAL)
    macroEntry.delete(0, 'end')
    macroEntry.insert(0, combo)


def connectSwitchChange():
    if (connectSwitch.get() == "on"):
        updatePorts()
    switchChange()


def switchChange():
    switchStates[0] = switch_1.get()
    switchStates[1] = switch_2.get()
    switchStates[2] = switch_3.get()
    switchStates[3] = connectSwitch.get()
    pickleData()


def upload_button_callback():
    logging.debug("Upload here")
    file_path, colors = imgPicker()

    if (file_path != NONE and colors != NONE):
        to_update = name_dict[combobox_1.get()]  # file name to send to serial

        # function which send the file
        imgSender(file_path, to_update, 0, colors)

        # if it is  a menu item also send a smaller image (done by adding border)
        if (to_update.decode()[0:4] == "menu"):
            withS = (to_update.decode()[:-1]+"s\n").encode()
            # function which send the smaller image this time
            imgSender(file_path, withS, 1, colors)


def runMacros():
    """
    Detect all button presses and window switching
    """
    # Connect to serial port #  (add gui and auto detect)
    if (ser.isOpen()):
        # send current app over serial
        if (switch_3.get() == "on"):
            try:
                sendWindow()  # function to send active window num to opendeck
            except:
                # can fail for many reasons: active window , serial.write fails
                logging.warning("Send Application Failed")

        # Read from serial port and handle events
        try:
            serialInput = ser.readline().decode().strip()
            if (len(serialInput) > 1):
                logging.debug(f'Serial message: "{serialInput}"')
            if (serialInput == ''):
                pass
            elif (len(serialInput) > 2):
                if (serialInput[0:6] == "Menu: "):
                    try:
                        number = int(serialInput[6:])
                    except Exception as error:
                        logging.warning(
                            f"Couldn't decode number {number}: {error}")
                    handleSerialCommandMenuNumber(number)
            else:
                try:
                    number = int(serialInput)
                except Exception as error:
                    logging.warning(
                        f"Couldn't decode number {number}: {error}")
                handleSerialCommandNumber(number)
        except Exception as error:  # error reading from buffer so close serial to try and re-connect
            logging.error("Error reading line: {error}")
            ser.close()


def handleSerialCommandMenuNumber(number):
    """
    Handle "Menu: X" events, where X is the app number
    """
    if (switch_1.get() == "on"):
        bringWindowFront(number)


modifier_keys = {
    "cmd": Key.cmd,
    "alt": Key.alt,
    "ctrl": Key.ctrl,
    "shift": Key.shift,
    "esc": Key.esc,
    "tab": Key.tab,
    "windows": Key.cmd,
    "right": Key.right,
    "left": Key.left,
}


def handleSerialCommandNumber(number):
    """
    Handle number events, where the number represents the macro button
    """
    # Set window to app button was for
    appNum = math.ceil(number/3)
    if (app_dict[appNum] != "" and switch_2.get() == "on"):
        bringWindowFront(appNum)
    # Run the macros
    logging.info(f"Running macro {number}: {key_dict[number][1]}")
    for command in key_dict[number][0]:
        logging.info(f"Command: {command}")
        keys = command.split("+")
        for i in range(len(keys)):
            if keys[i] in modifier_keys:
                logging.debug(f"Replacing {keys[i]} with modifier")
                keys[i] = modifier_keys[keys[i]]
        try:
            for i in range(len(keys)):
                logging.debug(f"Pressing {keys[i]}")
                keyboard.press(keys[i])
            for i in reversed(range(len(keys))):
                logging.debug(f"Releasing {keys[i]}")
                keyboard.release(keys[i])
            time.sleep(0.1)
        except IndexError as error:
            logging.warning(f"Unsupported key in command `{command}`: {error}")
        except ValueError as error:
            logging.warning(
                f"Unrecognized hotkey in command `{command}`: {error}")
        except Exception as error:
            logging.error(f"Failed to run command `{command}`: {error}")


def bringWindowFront(num):
    """
    Make chosen app/window active, where num represents the app number
    """
    if sys.platform in ['Windows', 'win32', 'cygwin']:
        # could be an issue if multiple instances are open and it uses
        # background one instead of active one (could scan all to see if one
        # is already open)
        title = app_dict[num]
        if (title != ""):
            try:
                if (len(gw.getWindowsWithTitle(title)) > 0):  # check if application is open
                    window = gw.getWindowsWithTitle(title)[0]
                    if (window.isMinimized):
                        window.restore()  # if minimized then open
                    else:
                        window.activate()  # if already open bring to front
                    return True
            except Exception as error:
                logging.warning("Failed to bring window to front: {error}")
                return False
    elif sys.platform in ['Mac', 'darwin', 'os2', 'os2emx']:
        # To Do: https://stackoverflow.com/questions/10266281/obtain-active-window-using-python
        return False


lastWindow = ""


def sendWindow():
    """
    Send active window to deck
    """
    global lastWindow
    activeWindow = gw.getActiveWindow().title()
    if (activeWindow != lastWindow):  # if window changed
        logging.info(f"window changed to {activeWindow}")
        lastWindow = activeWindow
        for item in app_dict:
            appName = app_dict[item]
            if (appName != ""):  # loop through all app names
                if appName.lower() in lastWindow.lower():  # if name of app in current window send menu num
                    # return menu number it was found on
                    logging.info(
                        f"Sending serial command: `GoTo: {str(item)}`")
                    if (ser.isOpen()):
                        ser.write(("GoTo: " + str(item)).encode("utf-8"))
                        time.sleep(0.2)
                    break


def imgPicker():
    """
    Image upload file selector
    """
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    logging.debug(f"Image picker: opened `{file_path}`")
    if (file_path):
        colors = askcolor(title="Tkinter Color Chooser")
        logging.debug(f"Image picker: color chosen: `{colors[0]}`")
    return (file_path, colors)


def imgSender(file_path, image, border, colors):
    """
    Given an image, convert to deck format and send data over the serial port
    """
    global ser
    logging.debug(f"imgSender: {image}")

    # Convert colours to byte array
    colour = bytearray()
    colour = [colors[0][0], colors[0][1], colors[0][2]]  # colour in RGB

    img = cv2.imread(file_path, 0)

    # Resize image to correct width
    height, width = img.shape
    logging.debug(f"imgSender: {width} x {height}")

    if (width != 54):
        scale_factor = 54/width
        new_height = int(height*scale_factor)
        dim = (int(54), int(new_height))
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    height, width = img.shape

    # add empty border to make a smaller image, used to indicate when button is pressed
    if (border):
        img = cv2.copyMakeBorder(src=img, top=10, bottom=10, left=10,
                                 right=10, borderType=cv2.BORDER_CONSTANT, value=[255, 255, 255])
        height, width = img.shape
        if (width != 54):  # do this for a second time to
            scale_factor = 54/width
            new_height = int(height*scale_factor)
            dim = (int(54), int(new_height))
            img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    height, width = img.shape
    logging.debug(f"imgSender: {width} x {height}")

    # crop the image
    # height that image starts at is taller than 70 px (to center it)
    crop_height = 0
    start_height = 0  # where the image starts if less than 70px (to center it)
    max_height = 70  # if the image less than 70px stop at end of image
    if (height > 70):  # if image larger than 70 high after resize then centre it
        crop_height = int((height-70)/2)
    elif (height < 70):
        start_height = int((70-height)/2)
        max_height = height

    # convert to black and white from 0 to 1
    img_reverted = cv2.bitwise_not(img)
    new_img = img_reverted / 255.0

    mono_img_width = ((54//8+1)*8)
    mono_img = np.zeros((70, mono_img_width))
    logging.debug(f"imgSender: {mono_img}")

    # convert numpy array into 0 and 1 (mono colour) (puts image into centre of height as well)
    for y in range(0, max_height):
        for x in range(0, 54):
            # if compare pixel to threshold (make selectable in future with slider)
            if (new_img[y+crop_height][x] < 0.5):
                mono_img[y+start_height][x] = 0
            else:
                mono_img[y+start_height][x] = 1

    outputArray = []
    # convert into binary bmp format
    for y in range(0, 70):
        for x in range(0, mono_img_width, 8):
            if (y < start_height or y > (start_height + height)):
                binary = "00000000"  # make outside pixels empty
            else:
                # turn 8 pixels into one hex number
                binary = str(int(mono_img[y][x]))+str(int(mono_img[y][x+1]))+str(int(mono_img[y][x+2]))+str(int(mono_img[y][x+3]))+str(
                    int(mono_img[y][x+4]))+str(int(mono_img[y][x+5]))+str(int(mono_img[y][x+6]))+str(int(mono_img[y][x+7]))
            # Print in format stored in arduino
            print("0x{:02x},".format(int(binary, 2)), end=' ')
            outputArray.append(int(binary, 2))
        # Carriage return for correct arduino array formatting
        print("\r")

    # print the final image array
    # print(outputArray)

    if (ser.isOpen()):
        # sent image and colour to serial port
        # ser = serial.Serial(portSelect.get(), baudSelect.get())
        time.sleep(0.5)
        ser.write(image)
        serialInput = ser.readline().decode().strip()
        logging.debug(f'Serial message: "{serialInput}"')
        packet = bytearray()
        packet = outputArray
        ser.write(packet)
        time.sleep(0.2)
        ser.write(colour)
        # time.sleep(0.5)

    # Visualize the result
    # plt.imshow(mono_img, cmap='gray')
    # plt.xlim(0,54)
    # plt.show()


# GUI setup
app.grid_rowconfigure(0, weight=1, minsize=200)
app.grid_columnconfigure(0, weight=1, minsize=200)


ports = serial.tools.list_ports.comports()
COMports = ["Select"]
for port, desc, hwid in sorted(ports):
    COMports.append(port+": "+desc)
    # COMports.append(port)


#   Connections settings #Add turn auto detect on/off #add turn on/off and connection status
frame_1 = customtkinter.CTkFrame(master=app)
frame_1.pack(pady=(20, 20), padx=60, fill="both", expand=False)

frame_1.grid_columnconfigure(0, weight=1)
frame_1.grid_columnconfigure(1, weight=1)

topLabel = customtkinter.CTkLabel(
    master=frame_1, justify=tkinter.LEFT, text="Connection Settings")
topLabel.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
topLabel.configure(font=("Arial", 22))


portLabel = customtkinter.CTkLabel(
    master=frame_1, justify=tkinter.LEFT, text="Select Port:")
portLabel.grid(row=1, column=0, columnspan=1, padx=0, pady=10, sticky="e")

portSelect = customtkinter.CTkComboBox(frame_1, values=COMports)
portSelect.grid(row=1, column=1, columnspan=1, padx=0, pady=10, sticky="w")

baudLabel = customtkinter.CTkLabel(
    master=frame_1, justify=tkinter.LEFT, text="Select Baud Rate:")
baudLabel.grid(row=2, column=0, columnspan=1, padx=20, pady=10, sticky="e")

baudSelect = customtkinter.CTkComboBox(frame_1, values=["9600", "115200"])
baudSelect.grid(row=2, column=1, columnspan=1, padx=0, pady=10, sticky="w")
baudSelect.set("115200")

connectSwitchState = customtkinter.StringVar(value=switchStates[3])
connectSwitch = customtkinter.CTkSwitch(master=frame_1, text="Auto Detect Port",
                                        command=connectSwitchChange, variable=connectSwitchState, onvalue="on", offvalue="off")
connectSwitch.grid(row=3, column=0, columnspan=2,
                   padx=20, pady=(0, 10), sticky="nn")

connectLabel = customtkinter.CTkLabel(
    master=frame_1, justify=tkinter.LEFT, text="Not Connected", text_color="red")
connectLabel.grid(row=4, column=0, columnspan=2,
                  padx=20, pady=(0, 10), sticky="ew")
connectLabel.configure(font=("Arial", 16))

# auto detect port (make function in future)
if (connectSwitch.get() == "on"):
    detectPort(ports)


# Image Upload
frame_4 = customtkinter.CTkFrame(master=app)
frame_4.pack(pady=(0, 20), padx=60, fill="both", expand=False)

frame_4.grid_columnconfigure(0, weight=1)
frame_4.grid_columnconfigure(1, weight=1)

label_1 = customtkinter.CTkLabel(
    master=frame_4, justify=tkinter.LEFT, text="Image Upload")
label_1.grid(row=0, column=0, columnspan=2,
             padx=20, pady=(10, 10), sticky="ew")
label_1.configure(font=("Arial", 22))

combobox_1 = customtkinter.CTkComboBox(frame_4, values=OPTIONS)
combobox_1.grid(row=1, column=0, columnspan=2, padx=200, pady=10, sticky="ew")
combobox_1.set("Home 1")

button_1 = customtkinter.CTkButton(
    master=frame_4, command=upload_button_callback, text="Select & Upload")
button_1.grid(row=2, column=0, columnspan=2, padx=200, pady=10, sticky="ew")

# Macro Setup                         #add record keystrokes!!!!!!!!!!
frame_2 = customtkinter.CTkFrame(master=app)
frame_2.pack(pady=(0, 20), padx=60, fill="both", expand=False)

frame_2.grid_columnconfigure(0, weight=1)
frame_2.grid_columnconfigure(1, weight=1)
frame_2.grid_columnconfigure(2, weight=1)
frame_2.grid_columnconfigure(3, weight=1)

topLabel = customtkinter.CTkLabel(
    master=frame_2, justify=tkinter.LEFT, text="Macro Setup")
topLabel.grid(row=3, column=0, columnspan=4, padx=20, pady=10, sticky="ew")
topLabel.configure(font=("Arial", 22))

topLabel = customtkinter.CTkLabel(
    master=frame_2, justify=tkinter.LEFT, text="Button Number")
topLabel.grid(row=4, column=0, columnspan=1, padx=20, pady=0, sticky="ew")
macroCombobox = customtkinter.CTkComboBox(
    frame_2, values=BUTTON_OPTIONS, command=macroCombobox_callback)
macroCombobox.grid(row=5, column=0, columnspan=1,
                   padx=20, pady=(0, 0), sticky="ew")

topLabel = customtkinter.CTkLabel(
    master=frame_2, justify=tkinter.LEFT, text="Macro's")
topLabel.grid(row=4, column=1, columnspan=1, padx=10, pady=0, sticky="ew")
macroEntry = customtkinter.CTkEntry(master=frame_2)
macroEntry.grid(row=5, column=1, columnspan=1,
                padx=10, pady=(0, 0), sticky="ew")
if (len(key_dict[1][0]) > 1):
    for item in key_dict[1][0]:
        macroEntry.insert(0, (item+','))
else:
    macroEntry.insert(0, key_dict[1][0])
recButton = customtkinter.CTkButton(
    master=frame_2, command=macro_record, text="Record Keys (5 Sec)")
recButton.grid(row=6, column=1, columnspan=1,
               padx=10, pady=(10, 20), sticky="ew")

topLabel = customtkinter.CTkLabel(
    master=frame_2, justify=tkinter.LEFT, text="Nickname")
topLabel.grid(row=4, column=2, columnspan=1, padx=10, pady=0, sticky="ew")
nameEntry = customtkinter.CTkEntry(master=frame_2)
nameEntry.grid(row=5, column=2, columnspan=1,
               padx=10, pady=(0, 0), sticky="ew")
nameEntry.insert(0, key_dict[1][1])

button_1 = customtkinter.CTkButton(
    master=frame_2, command=macro_update, text="Update")
button_1.grid(row=5, column=3, columnspan=1, padx=20, pady=(0, 0), sticky="ew")

# App Setup and window Switching
frame_3 = customtkinter.CTkFrame(master=app)
frame_3.pack(pady=(0, 20), padx=60, fill="both", expand=True)

frame_3.grid_columnconfigure(0, weight=1)
frame_3.grid_columnconfigure(1, weight=1)
frame_3.grid_columnconfigure(2, weight=1)

topLabel = customtkinter.CTkLabel(
    master=frame_3, justify=tkinter.LEFT, text="Application Setup")
topLabel.grid(row=5, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
topLabel.configure(font=("Arial", 22))

topLabel = customtkinter.CTkLabel(
    master=frame_3, justify=tkinter.LEFT, text="App Number")
topLabel.grid(row=6, column=0, columnspan=1, padx=20, pady=0, sticky="ew")
appCombobox = customtkinter.CTkComboBox(
    frame_3, values=HOME_OPTIONS, command=appCombobox_Callback)
appCombobox.grid(row=7, column=0, columnspan=1,
                 padx=20, pady=(0, 0), sticky="ew")
# appCombobox.set("CTkComboBox")

topLabel = customtkinter.CTkLabel(
    master=frame_3, justify=tkinter.LEFT, text="App Name")
topLabel.grid(row=6, column=1, columnspan=1, padx=20, pady=0, sticky="ew")
appEntry = customtkinter.CTkEntry(master=frame_3)
appEntry.grid(row=7, column=1, columnspan=1, padx=20, pady=(0, 0), sticky="ew")
appEntry.insert(0, app_dict[1])

appUpdate = customtkinter.CTkButton(
    master=frame_3, command=app_update, text="Update")
appUpdate.grid(row=7, column=2, columnspan=1,
               padx=20, pady=(0, 0), sticky="ew")

# switches
sw1State = customtkinter.StringVar(value=switchStates[0])
switch_1 = customtkinter.CTkSwitch(master=frame_3, text="Menu Change Opens Computer App",
                                   command=switchChange, variable=sw1State, onvalue="on", offvalue="off")
switch_1.grid(row=8, column=0, columnspan=3,
              padx=20, pady=(20, 10), sticky="nn")

sw2State = customtkinter.StringVar(value=switchStates[1])
switch_2 = customtkinter.CTkSwitch(master=frame_3, text="Macro Button Opens Computer App",
                                   command=switchChange, variable=sw2State, onvalue="on", offvalue="off")
switch_2.grid(row=9, column=1, columnspan=1, padx=20, pady=10, sticky="nn")

sw3State = customtkinter.StringVar(value=switchStates[2])
switch_3 = customtkinter.CTkSwitch(master=frame_3, text="Deck Shows Current Active App",
                                   command=switchChange, variable=sw3State, onvalue="on", offvalue="off")
switch_3.grid(row=10, column=1, columnspan=1, padx=20, pady=10, sticky="nn")

# label for buttons numbers
butNumLabel = customtkinter.CTkLabel(
    master=frame_3, justify=tkinter.LEFT, text="Buttons 1, 2, 3")
butNumLabel.grid(row=8, column=0, columnspan=1, padx=0, pady=0, sticky="nn")
butNumLabel.configure(font=("Arial", 10))


# Threading (actually running everything)

# Using threading to display GUI and send macros at same time (May be use a fair amount of memory on a slow computer)
def threading():
    # Call work function
    t1 = Thread(target=work)
    t1.start()


def work():
    while (stop == False):  # this method runs smoother but throws an error on exit
        updatePorts()  # updates port list and handle serial connection
        runMacros()  # function to detect all key presses and window switching


stop = False


def main():
    threading()
    app.mainloop()
    stop = True


if __name__ == "__main__":
    main()
