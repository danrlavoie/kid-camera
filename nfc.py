import os

from dotenv import load_dotenv
from PIL import Image

# Takes care of setting up a specialized picture directory for an NFC card
# Given an NFC identifier, when it's initialized, it makes a directory,
# if one doesn't already exist, for the given NFC card, in the base picture dir.
# It also provides the filepath as a property so other classes can use it to,
# for example, look up pics.
# If no id is provided in the init, this is like starting the camera without
# an NFC card - it sets up a default pics directory.
class NFC():
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
        self.position = 0

    def deactivate_id(self):
        self.activate_id("default")

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

    def __init__(self, base_dir, id="default"):
        self.base_dir = base_dir
        print("Hello, NFC #" + id)
        self.activate_id(id)

    def loadImage(self):
        current_gallery_files = [name for name in os.listdir(self._pic_path) if os.path.isfile(os.path.join(self._pic_path,name))]
        # This will fail if the directory has no pictures in it
        fileName = current_gallery_files[self.position]
        image = Image.open(os.path.join(self._pic_path, fileName))
        return image

if __name__ == '__main__':
    load_dotenv()
    nfc = NFC(os.getenv('BASE_PIC_PATH'))
    image = nfc.loadImage()
    # Resize the image for display
    image = image.resize((640, 480))
    image.show()
