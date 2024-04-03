from picamera2 import Picamera2, Preview
from libcamera import Transform
import sys
import time
import datetime

class MyApp():
    def __init__(self):
        print("init")
        self.cam = Picamera2()

    def run(self):
        print("run")
        self.cam.start_preview(Preview.QTGL)
        self.cam.start()
        time.sleep(3)
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.jpg")
        self.cam.capture_file(filename)

        self.cam.stop_preview()
        time.sleep(3)
        self.cam.start_preview(Preview.QTGL)
        time.sleep(3)


if __name__ == "__main__":
    app = MyApp()
    app.run()
    sys.exit()