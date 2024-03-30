import os

import pathlib
from dotenv import load_dotenv
from PIL import Image
import cv2

from kctypes import Direction

# Takes care of setting up a specialized picture directory for an NFC card
# Given an NFC identifier, when it's initialized, it makes a directory,
# if one doesn't already exist, for the given NFC card, in the base picture dir.
# It also provides the filepath as a property so other classes can use it to,
# for example, look up pics.
# If no id is provided in the init, this is like starting the camera without
# an NFC card - it sets up a default pics directory.
class NFC():
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value

    @property
    def pic_path(self):
        return self._pic_path
    @pic_path.setter
    def pic_path(self, value):
        self._pic_path = value

    # Store the last position for each gallery or else use 0
    @property
    def position(self):
        return self._position

    def __init__(self, base_dir, id="default"):
        self.base_dir = base_dir
        print("Hello, NFC #" + id)
        self.activate_id(id)

    def maybe_create_picture_directory(self):
        # Confirm that the base picture directory exists
        if (os.path.exists(self.base_dir)):
            # Then see if a subdir for this nfc id doesn't exist
            if not (os.path.exists(self._pic_path)):
                # Create the folder
                os.makedirs(self._pic_path)
        else:
            # this is bad, we should already have a pics folder
            print("NO PIC FOLDER FOUND")

    def activate_id(self, id):
        self._id = id
        self._pic_path = os.path.join(self.base_dir, self._id)
        self.maybe_create_picture_directory()
        self.gallery_size = len([name for name in os.listdir(self._pic_path) if os.path.isfile(os.path.join(self._pic_path,name))])
        self._position = 0

    def deactivate_id(self):
        self.activate_id("default")

    def load_image(self):
        current_gallery_files = [name for name in os.listdir(self._pic_path) if os.path.isfile(os.path.join(self._pic_path,name))]
        # This will fail if the directory has no pictures in it
        filename = current_gallery_files[self._position]
        extension = pathlib.Path(filename).suffix
        return {
            "filename": os.path.join(self._pic_path,filename),
            "extension": extension
        }

    def gallery_scroll(self, direction):
        if direction == Direction.FWD:
            self._position += 1
            if self._position >= self.gallery_size:
                self._position = 0
        else:
            self._position -= 1
            if self._position <0:
                self._position = self.gallery_size - 1
        

if __name__ == '__main__':
    load_dotenv()
    nfc = NFC(os.getenv('BASE_PIC_PATH'))
    image = nfc.load_image()
    # Resize the image for display
    # opencv
    cv2.namedWindow('pic-display', cv2.WINDOW_NORMAL )
    cv2.setWindowProperty('pic-display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty('pic-display', cv2.WND_PROP_TOPMOST, 1)
    image = cv2.resize(image, (640, 480))
    cv2.imshow('pic-display', image)
    cv2.waitKey(0)
    print("GOT HERE")
    # PIL
    # image = image.resize((640, 480))
    # image.show()
"""
vid = cv2.VideoCapture(0)
while(True):
  ret, frame = vid.read()
  cv2.imshow('frame', frame)
  # when 'x' key is pressed the video capture stops
  if cv2.waitKey(1) & 0xFF == ord('x'):
    break
vid.release()
cv2.destroyAllWindows()
"""
