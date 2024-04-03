from picamera2 import Picamera2, Preview
from libcamera import Transform
import sys

class MyApp():
    def __init__(self):
        print("init")
        self.cam = Picamera2()

    def run(self):
        print("run")
        self.cam.start_preview(Preview.QTGL)
        self.cam.start()


if __name__ == "__main__":
    app = MyApp()
    app.run()
    sys.exit()