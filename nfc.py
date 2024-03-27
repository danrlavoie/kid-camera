import os
from dotenv import load_dotenv

# Takes care of setting up a specialized picture directory for an NFC card
# Given an NFC identifier, when it's initialized, it makes a directory,
# if one doesn't already exist, for the given NFC card, in the base picture dir.
# It also provides the filepath as a property so other classes can use it to,
# for example, look up pics.
# If no id is provided in the init, this is like starting the camera without
# an NFC card - it sets up a default pics directory.
class NFC():
    def maybe_create_picture_directory(self, base_dir):
        # Confirm that the base picture directory exists
        if (os.path.exists(base_dir)):
            # Then see if a subdir for this nfc id doesn't exist
            if not (os.path.exists(self.pic_path)):
                # Create the folder
                os.makedirs(self.pic_path)
        else:
            # this is bad, we should already have a pics folder
            print("NO PIC FOLDER FOUND")
    @property
    def pic_path(self):
        return self._pic_path
    @pic_path.setter
    def pic_path(self, value):
        self._pic_path = value
    def __init__(self, base_dir, id="default"):
        print("Hello, NFC #" + id)
        self.id = id
        self.pic_path = os.path.join(base_dir, self.id)
        self.maybe_create_picture_directory(base_dir)

if __name__ == '__main__':
    load_dotenv()
    nfc = NFC(os.getenv('BASE_PIC_PATH'))
