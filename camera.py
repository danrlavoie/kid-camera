import cv2
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
        fullscreen = os.getenv('FULLSCREEN')
        pygame.init()
        if fullscreen == 1:
            self.canvas = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
        else:
            self.canvas = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        self.playing_video_file = None
        self.playing_video_fps = -1
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
            self.clock.tick(self.playing_video_fps)
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
                self.canvas.fill((92,106,114))
                # Get and display image at current position
                res = self.nfc.load_image()
                filename = res["filename"]
                extension = res["extension"]
                if (not extension == ".mp4"):
                    image = pygame.image.load(filename)
                    image = pygame.transform.scale(image, (640, 480))
                    self.canvas.blit(image, dest = (0,0))
                # If a video, make sure it loops
                else:
                    if (not self.playing_video_file):
                        self.playing_video_file = cv2.VideoCapture(filename)
                        self.playing_video_fps = self.playing_video_file.get(cv2.CAP_PROP_FPS)
                    success, video_image = self.playing_video_file.read()
                    if success:
                        video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "BGR")
                        video_surf = pygame.transform.scale(video_surf, (640,480))
                        self.canvas.blit(video_surf, (0,0))
                    else:
                        # Likely the end of the video frame, loop back to start
                        self.playing_video_file.set(cv2.CAP_PROP_POS_FRAMES, 0)
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
                        self.playing_video_file = None
                    if event.key == pygame.K_RIGHT:
                        self.nfc.gallery_scroll(Direction.FWD)
                        self.playing_video_file = None
                    if event.key == pygame.K_q:
                        self.running = False
            pygame.display.flip()
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
