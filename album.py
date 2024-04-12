import logging
import os
import pathlib
import cv2

from kctypes import Direction
import constants

logger = logging.getLogger(__name__)
# Takes care of setting up a specialized picture directory for an NFC card
# Given an NFC identifier, when it's initialized, it makes a directory,
# if one doesn't already exist, for the given NFC card, in the base picture dir.
# It also provides the filepath as a property so other classes can use it to,
# for example, look up pics.
# If no id is provided in the init, this is like starting the camera without
# an NFC card - it sets up a default pics directory.
class Album():
    # id is the unique identifier present with a given NFC card.
    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        self._id = value

    # pick path is the filepath for pictures for the current NFC card (or default)
    @property
    def pic_path(self):
        return self._pic_path
    @pic_path.setter
    def pic_path(self, value):
        self._pic_path = value

    # Store the current position for each gallery or else use 0
    @property
    def position(self):
        return self._position

    def __init__(self, base_dir, id="default"):
        logger.debug('Function Album __init__')
        logger.debug('Received %s as base_dir for NFC card', base_dir)
        logger.debug('Received %s as id for NFC card', id)
        self.base_dir = base_dir
        self.activate_id(id)

    def maybe_create_picture_directory(self):
        """
        maybe_create_picture_directory will set up, if it doesn't exist yet,
        a directory within the base directory to match the current pic path.
        If it checks and the directory already exists, it does nothing.
        """
        logger.debug('Function maybe_create_picture_directory')
        # Confirm that the base picture directory exists
        if (not os.path.exists(self.base_dir)):
            logger.info('Did not find directory %s', self.base_dir)
            logger.info('Creating directory %s', self.base_dir)
            os.makedirs(self.base_dir)
        # Then see if a subdir for this nfc id doesn't exist
        if not (os.path.exists(self._pic_path)):
            logger.info('Did not find directory %s', self._pic_path)
            logger.info('Creating directory %s', self._pic_path)
            # Create the folder
            os.makedirs(self._pic_path)

    def activate_id(self, id):
        """
        activate_id sets up the given NFC card id for picture storage.
        It sets the given id as the active id, gets a filepath location for
        storing images, and sets up pointers for wayfinding while viewing
        files in gallery mode.
        @param id the id of the NFC card to activate, or the string 'default'
        """
        logger.debug('Function activate_id')
        self._id = id
        self._pic_path = os.path.join(self.base_dir, self._id)
        logger.info('Ensuring that combined filepath %s exists for usage', self._pic_path)
        self.maybe_create_picture_directory()
        logger.info('Setting gallery file index to 0')
        self._position = 0

    def deactivate_id(self):
        """
        deactivate_id removes the currently-associated NFC card id from the
        program state. Functionally this is just activating an NFC card with
        the id 'default' instead of an actual NFC card id.
        When no NFC card is connected to the system, teh default directory is
        used to store gallery files.
        """
        logger.debug('Function deactivate_id')
        self.activate_id("default")

    def load_image(self):
        """
        load_image grabs the filename and extension for the file in the current
        gallery _pic_path filepath, at the current _position index in the file
        list, and returns them.
        The function is called load_image, but it'll load any kind of file, so
        be careful to only store images or videos in these folders.
        """
        logger.debug('Function load_image')
        logger.debug('Fetching list of files in the gallery directory')
        current_gallery_files = [name for name in os.listdir(self._pic_path) if os.path.isfile(os.path.join(self._pic_path,name))]
        # This will fail if the directory has no pictures in it
        logger.debug('Fetching filename of file at position %s', self._position)
        filename = current_gallery_files[self._position]
        extension = pathlib.Path(filename).suffix
        logger.info('Found filename %s with extension %s', filename, extension)
        return {
            "filename": os.path.join(self._pic_path,filename),
            "extension": extension
        }

    def gallery_scroll(self, direction):
        """
        gallery_scroll steps forward or backward through the current gallery
        directory by incrementing or decrementing the _position variable.
        @param direction a Direction enum, either Direction.FWD or Direction.REV
        """
        logger.debug('Function gallery_scroll')
        logger.debug('Calculating current size of list of files in the gallery directory')
        self.gallery_size = len([name for name in os.listdir(self._pic_path) if os.path.isfile(os.path.join(self._pic_path,name))])
        if direction == Direction.FWD:
            logger.debug('Moving forward in gallery')
            self._position += 1
            if self._position >= self.gallery_size:
                self._position = 0
            logger.info('New file index is %s', self._position)
        else:
            logger.debug('Moving backward in gallery')
            self._position -= 1
            if self._position <0:
                self._position = self.gallery_size - 1
            logger.info('New file index is %s', self._position)
        

if __name__ == '__main__':
    album = Album(constants.BASE_PIC_PATH)
    image = album.load_image()
    cv2.namedWindow('pic-display', cv2.WINDOW_NORMAL )
    cv2.setWindowProperty('pic-display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty('pic-display', cv2.WND_PROP_TOPMOST, 1)
    image = cv2.resize(image, (640, 480))
    cv2.imshow('pic-display', image)
    cv2.waitKey(0)

