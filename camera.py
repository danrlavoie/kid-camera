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
        font = pygame.font.Font('SauceCodeProNerdFont-Regular.ttf', 32)
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
        """
        run is the main "game" loop of the program. It gathers the current
        program state, makes necessary state updates, renders graphics onto
        the screen, handles any new events, and then loops to start again.
        It will run indefinitely as long as the running var is true.
        """
        while (self.running):
            self.clock.tick(self.playing_video_fps)
            if (not self.recording):
                self.set_current_mode()
            else:
                # If recording, see if it's time to stop recording
                delta = datetime.now() - self.last_capture_timestamp
                if (delta > presentation_timeout):
                    self.recording = false
                    # Save the recording to a file
            self.handle_nfc_card()
            if (self.display_mode == DisplayMode.GALLERY):
                self.render_gallery()
            else:
                self.render_camera_feed()
            self.handle_events()
            pygame.display.flip()

    def set_current_mode(self):
        """
        set_current_mode checks the current position of the four position mode
        selector switch. It uses that position to determine which camera should
        be active and whether to set up for recording video or still images. It
        also checks whether the mode has changed since the last frame, and uses
        that check to determine if the app needs to be in capture mode.
        """
        if self.input.active_pos() == SelectorPosition.ONE:
            self.camera = Camera.SELFIE
            self.capture_mode = CaptureMode.PICTURE
        elif self.input.active_pos() == SelectorPosition.TWO:
            self.camera = Camera.SELFIE
            self.capture_mode = CaptureMode.VIDEO
        elif self.input.active_pos() == SelectorPosition.THREE:
            self.camera = Camera.FORWARD
            self.capture_mode = CaptureMode.PICTURE
        elif self.input.active_pos() == SelectorPosition.FOUR:
            self.camera = Camera.FORWARD
            self.capture_mode = CaptureMode.VIDEO
        if (not self.input.active_pos() == self.active_pos):
            # This checks if we've changed 4pos modes
            # If so, we should ensure we are in capture mode
            # Otherwise we have no way to return from gallery
            self.active_pos = self.input.active_pos()
            self.display_mode == DisplayMode.CAPTURE

    def handle_nfc_card(self):
        """
        handle_nfc_card contains the I/O logic for detecting the presence of an
        NFC data card on the camera. If it finds one, it activates it - and it
        deactivates any current NFC card if none is found. This function does
        nothing if the detected state matches the preexisting NFC state.
        """
        # Look for an NFC card - if found, check that it is active
        found_nfc = None
        if (found_nfc):
            if not (found_nfc == self.nfc.id):
                self.nfc.activate_id(found_nfc)
        # If none found, deactivate it
        else:
            if (not self.nfc.id == "default"):
                self.nfc.deactivate_id()

    def render_gallery(self):
        """
        render_gallery renders the image or video playback onto the screen.
        It begins by fetching a file from the current storage directory.
        If it's an image, it gets scaled to the device size and sent to the
        canvas for rendering.
        If a video is detected, OpenCV is used to stream the video - of note,
        the video's calculated FPS is used to set a periodic timer in pygame,
        so that the video can correctly play frame-by-frame.
        The video is also scaled to device size and rendered onto the canvas.
        When a video finishes playing, it will loop continuously.
        """
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
 
    def render_camera_feed(self):
        if (self.recording):
            recording_text = font.render('RECORDING', True, (211,198,170))
            recording_rect = recording_text.get_rect()
            recording_rect.center = (500, 100)
            self.canvas.blit(recording_text, recording_rect)
            # If recording a video, can show indicator
            # If recording and the time limit is reached, stop
            # Then save the file
        if (self.camera == Camera.SELFIE):
            camera_text = font.render('Selfie Cam', True, (211,198,170))
            camera_rect = recording_text.get_rect()
            camera_rect.center = (500, 300)
            self.canvas.blit(camera_text, camera_rect)
            # Disable forward cam
            # Enable selfie cam
            # Display selfie cam preview
        else:
            camera_text = font.render('Selfie Cam', True, (211,198,170))
            camera_rect = recording_text.get_rect()
            camera_rect.center = (500, 300)
            self.canvas.blit(camera_text, camera_rect)
            # Disable selfie cam
            # Enable forward cam
            # Display forward cam preview

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYUP:
                # ENCODER: Left and Right arrows
                if event.key == pygame.K_LEFT:
                    self.action_rotate_encoder(Direction.REV)
                if event.key == pygame.K_RIGHT:
                    self.action_rotate_encoder(Direction.FWD)
                # SELECTOR SWITCH: 1-4 numbers
                if event.key == pygame.K_1:
                    self.input.pos = 1
                if event.key == pygame.K_2:
                    self.input.pos = 2
                if event.key == pygame.K_3:
                    self.input.pos = 3
                if event.key == pygame.K_4:
                    self.input.pos = 4
                # CAPTURE BUTTON: c key
                if event.key == pygame.K_c:
                    pass
                # QUIT: q key
                if event.key == pygame.K_q:
                    self.running = False

    def action_rotate_encoder(self, dir):
        self.last_interaction = datetime.now()
        if self.display_mode == DisplayMode.CAPTURE:
            self.display_mode = DisplayMode.GALLERY
        else:
            # Increment or decrement current gallery position (with wrapping)
            self.nfc.gallery_scroll(dir)
            self.playing_video_file = None

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

if __name__ == "__main__":
    app = CameraApp()
    app.run()
