from datetime import datetime
import os

class Logger:
    def __init__(self, filename):
        if not os.path.exists(filename):
            file = open(filename, "w")
            file.close()

        self._filename = filename

    def write(self, message):
        current_time = datetime.now()
        current_time = current_time.strftime("%d.%m.%Y %H:%M:%S")

        print(current_time, message)
        with open(self._filename, "a") as f:
            f.write(current_time + " " + message + "\n")