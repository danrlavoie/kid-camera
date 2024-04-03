import os
import pathlib
import cv2

from kctypes import Direction
import constants

# Takes care of setting up a specialized picture directory for an NFC card
# Given an NFC identifier, when it's initialized, it makes a directory,
# if one doesn't already exist, for the given NFC card, in the base picture dir.
# It also provides the filepath as a property so other classes can use it to,
# for example, look up pics.
# If no id is provided in the init, this is like starting the camera without
# an NFC card - it sets up a default pics directory.
class NFC():
    # id is the unique identifier present with a given NFC card.
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value

    # pick path is the filepath for pictures for the current NFC card (or default)
    @property
    def cur_album_path(self):
        return self._cur_album_path
    @cur_album_path.setter
    def cur_album_path(self, value):
        self._cur_album_path = value

    # Store the current position for each gallery or else use 0
    @property
    def position(self):
        return self._position

    def __init__(self, base_dir, id="default"):
        self.base_dir = base_dir
        print("Hello, NFC #" + id)
        self.activate_id(id)

    def maybe_create_picture_directory(self):
        """
        maybe_create_picture_directory will set up, if it doesn't exist yet,
        a directory within the base directory to match the current pic path.
        If it checks and the directory already exists, it does nothing.
        """
        # Confirm that the base picture directory exists
        if (not os.path.exists(self.base_dir)):
            os.makedirs(self.base_dir)
        # Then see if a subdir for this nfc id doesn't exist
        if not (os.path.exists(self._cur_album_path)):
            # Create the folder
            os.makedirs(self._cur_album_path)

    def activate_id(self, id):
        """
        activate_id sets up the given NFC card id for picture storage.
        It sets the given id as the active id, gets a filepath location for
        storing images, and sets up pointers for wayfinding while viewing
        files in gallery mode.
        @param id the id of the NFC card to activate, or the string 'default'
        """
        self._id = id
        self._cur_album_path = os.path.join(self.base_dir, self._id)
        self.maybe_create_picture_directory()
        self._position = 0

    def deactivate_id(self):
        """
        deactivate_id removes the currently-associated NFC card id from the
        program state. Functionally this is just activating an NFC card with
        the id 'default' instead of an actual NFC card id.
        When no NFC card is connected to the system, teh default directory is
        used to store gallery files.
        """
        self.activate_id("default")

    def load_image(self):
        """
        load_image grabs the filename and extension for the file in the current
        gallery _cur_album_path filepath, at the current _position index in the file
        list, and returns them.
        The function is called load_image, but it'll load any kind of file, so
        be careful to only store images or videos in these folders.
        """
        current_gallery_files = [name for name in os.listdir(self._cur_album_path) if os.path.isfile(os.path.join(self._cur_album_path,name))]
        # This will fail if the directory has no pictures in it
        filename = current_gallery_files[self._position]
        extension = pathlib.Path(filename).suffix
        return {
            "filename": os.path.join(self._cur_album_path,filename),
            "extension": extension
        }

    def gallery_scroll(self, direction):
        """
        gallery_scroll steps forward or backward through the current gallery
        directory by incrementing or decrementing the _position variable.
        @param direction a Direction enum, either Direction.FWD or Direction.REV
        """
        self.gallery_size = len([name for name in os.listdir(self._cur_album_path) if os.path.isfile(os.path.join(self._cur_album_path,name))])
        if direction == Direction.FWD:
            self._position += 1
            if self._position >= self.gallery_size:
                self._position = 0
        else:
            self._position -= 1
            if self._position <0:
                self._position = self.gallery_size - 1
        

if __name__ == '__main__':
    nfc = NFC(constants.BASE_ALBUM_PATH)
    image = nfc.load_image()
    cv2.namedWindow('pic-display', cv2.WINDOW_NORMAL )
    cv2.setWindowProperty('pic-display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty('pic-display', cv2.WND_PROP_TOPMOST, 1)
    image = cv2.resize(image, (640, 480))
    cv2.imshow('pic-display', image)
    cv2.waitKey(0)

