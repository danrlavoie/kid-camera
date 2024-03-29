import os
import pygame
from datetime import datetime, timedelta
from dotenv import load_dotenv
# libcamera, libcamera-vid

from nfc import NFC
from gpioinput import GPIOInput
from keyboardinput import KeyboardInput
from kctypes import Camera, CaptureMode, DisplayMode, SelectorPosition, Direction

# A timeout of how long to show an image/gif after it finishes
presentation_timeout = timedelta(seconds = 5)

class CameraApp():
    def __init__(self):
        load_dotenv()
        pygame.init()
        self.canvas = pygame.display.set_mode((640, 480))
        self.running = True
        self.camera = Camera.SELFIE
        self.capture_mode = CaptureMode.PICTURE
        self.display_mode = DisplayMode.GALLERY
        self.active_pos = SelectorPosition.ONE
        # Whether a video is being recorded
        self.recording = False
        # The timestamp at which the last image was taken
        self.last_capture_timestamp = datetime.min
        # The timestamp at which the last button press occurred
        self.last_interaction = datetime.now
        self.nfc = NFC(os.getenv('BASE_PIC_PATH'))
        self.gpio_input = GPIOInput(self.action_rotate_encoder, self.action_capture)
        self.keyboard_input = KeyboardInput(self.action_rotate_encoder, self.action_capture)
        if (os.getenv('USE_KEYBOARD_INPUT')):
            self.input = self.keyboard_input
        else:
            self.input = self.gpio_input

    def run(self):
        while (self.running):
            # Main program loop
            # Check 4pos switch to have the right camera modes
            if (not self.recording):
                match self.input.active_pos():
                    case SelectorPosition.ONE:
                        self.camera = Camera.SELFIE
                        self.capture_mode = CaptureMode.PICTURE
                    case SelectorPosition.TWO:
                        self.camera = Camera.SELFIE
                        self.capture_mode = CaptureMode.VIDEO
                    case SelectorPosition.THREE:
                        self.camera = Camera.FORWARD
                        self.capture_mode = CaptureMode.PICTURE
                    case SelectorPosition.FOUR:
                        self.camera = Camera.FORWARD
                        self.capture_mode = CaptureMode.VIDEO
                if (not self.input.active_pos() == self.active_pos):
                    # This checks if we've changed 4pos modes
                    # If so, we should ensure we are in capture mode
                    # Otherwise we have no way to return from gallery
                    self.active_pos = self.input.active_pos()
                    self.display_mode == DisplayMode.CAPTURE
            else:
                # If recording, see if it's time to stop recording
                delta = datetime.now() - self.last_capture_timestamp
                if (delta > presentation_timeout):
                    self.recording = false
                    # Save the recording to a file
            # Look for an NFC card - if found, check that it is active
            found_nfc = None
            if (found_nfc):
                if not (found_nfc == self.nfc.id):
                    self.nfc.activate_id(found_nfc)
            # If none found, deactivate it
            else:
                if (not self.nfc.id == "default"):
                    self.nfc.deactivate_id()
            # Next, handle display logic
            if (self.display_mode == DisplayMode.GALLERY):
                # Get and display image at current position
                filename = self.nfc.load_image()
                image = pygame.image.load(filename)
                image = pygame.transform.scale(image, (640, 480))
                self.canvas.fill((92,106,114))
                self.canvas.blit(image, dest = (0,0))
                pass
                # If a video, make sure it loops
            else:
                # Hide picture gallery, then show camera feed
                if (self.recording):
                    pass
                    # If recording a video, can show indicator
                    # If recording and the time limit is reached, stop
                    # Then save the file
                if (self.camera == Camera.SELFIE):
                    pass
                    # Disable forward cam
                    # Enable selfie cam
                    # Display selfie cam preview
                else:
                    pass
                    # Disable selfie cam
                    # Enable forward cam
                    # Display forward cam preview
            # Render function here?
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.nfc.gallery_scroll(Direction.REV)
                    if event.key == pygame.K_RIGHT:
                        self.nfc.gallery_scroll(Direction.FWD)
            pygame.display.update()
    def action_rotate_encoder(self):
        self.last_interaction = datetime.now()
        if self.display_mode == DisplayMode.CAPTURE:
            self.display_mode = DisplayMode.GALLERY
        else:
            # Increment or decrement current gallery position (with wrapping)
            print("Need to change gallery position")

    def action_capture(self):
        self.last_interaction = datetime.now()
        self.last_capture_timestamp = datetime.now()
        if self.display_mode == DisplayMode.GALLERY:
            self.display_mode = DisplayMode.CAPTURE
        else:
            if self.capture_mode == CaptureMode.PICTURE:
                pass
                # Take a pic with current self.camera
            else:
                pass
                # Take a video with current self.camera

    def action_selector_change(self):
        pass
    def action_quit(self):
        exit()

    def render(self):
        print()

if __name__ == "__main__":
    app = CameraApp()
    app.run()
