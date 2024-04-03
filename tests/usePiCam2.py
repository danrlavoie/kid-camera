from picamera2 import Picamera2, Preview
from libcamera import Transform
import sys
import time
import datetime
import os.path
from picamera2.encoders import H264Encoder

class MyApp():
    def __init__(self):
        print("init")
        self.cam = Picamera2()
        self.path = "/home/me691kidcam/kid-camera/pics/default"

    def run(self):
        print("run")
        self.cam.start_preview(Preview.QTGL)
        self.cam.start()
        time.sleep(3)
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.jpg")
        filepath = os.path.join(self.path, filename)
        self.cam.capture_file(filepath)

        self.cam.stop_preview()
        time.sleep(3)
        
        self.cam.start_preview(Preview.QTGL)
        encoder = H264Encoder()
        self.cam.start_recording(encoder, '/home/me691kidcam/kid-camera/pics/temp/test.h264')
        time.sleep(3)
        self.cam.stop_recording()

        self.cam.stop_preview()
        self.cam.stop()

        


if __name__ == "__main__":
    app = MyApp()
    app.run()
    sys.exit()