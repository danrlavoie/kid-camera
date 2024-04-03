import cv2
import pygame
import pygame.camera
from datetime import datetime, timedelta
import sys
# libcamera, libcamera-vid
import subprocess

from nfc import NFC
from gpioinput import GPIOInput
from kctypes import Camera, CaptureMode, DisplayMode, SelectorPosition, Direction
import constants

# A timeout of how long to show an image/gif after it finishes
presentation_timeout = timedelta(seconds = 5)
ENCODER_ROTATED = pygame.USEREVENT + 1
CAPTURE_PRESSED = pygame.USEREVENT + 2

class CameraApp():
    def __init__(self):
        # First, Pygame setup
        fullscreen = constants.FULLSCREEN
        pygame.init()
        self.font = pygame.font.Font('SauceCodeProNerdFont-Regular.ttf', 32)
        if fullscreen == 1:
            self.canvas = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
        else:
            self.canvas = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()

        # Next, set up state variables
        self.running = True                         # Is the app running or not?
        self.playing_video_file = None              # If a video is playing on the screen, which video is it
        self.playing_video_fps = -1                 # What is the frames-per-second of the current video file
        self.camera = Camera.SELFIE                 # Whether selfie or forward facing camera is active
        self.capture_mode = CaptureMode.PICTURE     # Whether camera is recording pictures or video
        self.display_mode = DisplayMode.GALLERY     # Whether screen is showing camera or gallery
        self.active_pos = SelectorPosition.ONE      # Active position on the mode selector
        self.pos_override = None                    # Overriden mode selection, if using keyboard control
        self.recording = False                      # Whether a video is being recorded
        self.last_capture_timestamp = datetime.min  # The timestamp at which the last image was taken
        self.last_interaction = datetime.now        # The timestamp at which the last button press occurred

        #set up subprocess handlers
        self.previewProcess = None                  # For running libcamera-hello

        # Finally, set up the additional modules that plug into the main class
        self.nfc = NFC(constants.BASE_ALBUM_PATH)
        self.input = GPIOInput(self.post_custom_event, ENCODER_ROTATED, CAPTURE_PRESSED)

    def run(self):
        """
        run is the main "game" loop of the program. It gathers the current
        program state, makes necessary state updates, renders graphics onto
        the screen, handles any new events, and then loops to start again.
        It will run indefinitely as long as the running var is true.
        """
        while (self.running):
            self.clock.tick(self.playing_video_fps)
            # clear the canvas from the previous frame
            self.canvas.fill((92,106,114))
            if (not self.recording):
                self.set_current_mode()
            else:
                # If recording, see if it's time to stop recording
                delta = datetime.now() - self.last_capture_timestamp
                if (delta > presentation_timeout):
                    self.recording = False
                    # Save the recording to a file
                    print("Finished recording!")
            self.handle_nfc_card()
            if (self.display_mode == DisplayMode.GALLERY):
                self.render_gallery()
            else:
                self.render_camera_feed()
            self.handle_events()
            pygame.display.flip()
        # If not running anymore, quit the app
        pygame.quit()

    def set_current_mode(self):
        """
        set_current_mode checks the current position of the four position mode
        selector switch. It uses that position to determine which camera should
        be active and whether to set up for recording video or still images. It
        also checks whether the mode has changed since the last frame, and uses
        that check to determine if the app needs to be in capture mode.
        """
        position = self.input.active_pos(override=self.pos_override)
        if position == SelectorPosition.ONE:
            self.camera = Camera.SELFIE
            self.capture_mode = CaptureMode.PICTURE
        elif position == SelectorPosition.TWO:
            self.camera = Camera.SELFIE
            self.capture_mode = CaptureMode.VIDEO
        elif position == SelectorPosition.THREE:
            self.camera = Camera.FORWARD
            self.capture_mode = CaptureMode.PICTURE
        elif position == SelectorPosition.FOUR:
            self.camera = Camera.FORWARD
            self.capture_mode = CaptureMode.VIDEO
        if (not position == self.active_pos):
            # This checks if we've changed 4pos modes
            # If so, we should ensure we are in capture mode
            # Otherwise we have no way to return from gallery
            self.active_pos = position
            self.display_mode = DisplayMode.CAPTURE

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
                video_surf = pygame.image.frombuffer(video_image.tobytes(), video_image.shape[1::-1], "RGB")
                video_surf = pygame.transform.scale(video_surf, (640,480))
                self.canvas.blit(video_surf, (0,0))
            else:
                # Likely the end of the video frame, loop back to start
                self.playing_video_file.set(cv2.CAP_PROP_POS_FRAMES, 0)
 
    def render_camera_feed(self):
        """
        render_camera_feed renders what the current active camera sees onto the
        screen.
        It first checks whether to display the forward cam or selfie cam.
        Whichever camera is active has its image preview streamed to the screen.
        Next, it checks whether the device is in picture or video mode. A
        matching indicator is displayed to the screen.
        Then, it checks if the device is actively recording a video - if so, an
        indicator is displayed overlaying the screen.
        """
        #SELFIE OR FWD
        if (self.camera == Camera.SELFIE):
            camera_text = self.font.render('Selfie Cam', True, (211,198,170))
            camera_rect = camera_text.get_rect()
            camera_rect.center = (500, 300)
            self.canvas.blit(camera_text, camera_rect)
            # Disable forward cam
            if self.previewProcess is not None:
                self.previewProcess.terminate()
            self.canvas = pygame.display.set_mode((640, 480), pygame.HIDDEN)
            # Enable selfie cam and Display selfie cam preview
            self.previewProcess = subprocess.Popen(['libcamera-hello', '-t', '0', '--camera', constants.SELFIE_CAM_ID])
        else:
            camera_text = self.font.render('Forward Cam', True, (211,198,170))
            camera_rect = camera_text.get_rect()
            camera_rect.center = (500, 300)
            self.canvas.blit(camera_text, camera_rect)
            # Disable selfie cam
            if self.previewProcess is not None:
                self.previewProcess.terminate()
            self.canvas = pygame.display.set_mode((640, 480), pygame.HIDDEN)
            # Enable forward cam and Display forward cam preview
            self.previewProcess = subprocess.Popen(['libcamera-hello', '-t', '0', '--camera', constants.FWD_CAM_ID])

        # PIC OR VID    
        if (self.capture_mode == CaptureMode.PICTURE):
            capture_text = self.font.render('Picture Mode', True, (211,198,170))
            capture_rect = capture_text.get_rect()
            capture_rect.center = (150, 300)
            self.canvas.blit(capture_text, capture_rect)
        else:
            capture_text = self.font.render('Video Mode', True, (211,198,170))
            capture_rect = capture_text.get_rect()
            capture_rect.center = (150, 300)
            self.canvas.blit(capture_text, capture_rect)
        if (self.recording):
            recording_text = self.font.render('RECORDING', True, (211,198,170))
            recording_rect = recording_text.get_rect()
            recording_rect.center = (500, 100)
            self.canvas.blit(recording_text, recording_rect)
            # If recording a video, can show indicator


    def handle_events(self):
        """
        handle_events is where all the pygame events are processed for the app.
        Aside from the quit event, the app listens to the following events:
        - A custom ENCODER_ROTATED event mapping to a gpiozero Encoder
        - A custom CAPTURE_PRESSED event mapping to a gpiozero Button
        - Another option for quitting with the q key
        - Left and right arrow keys to simulate the encoder rotation
        - The c key to simulate the capture pressed behavior
        - Numbers 1-4 to override the mode switching feature in the gpiozero
          inputs.
        """
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
                    self.action_selector_change(1)
                if event.key == pygame.K_2:
                    self.action_selector_change(2)
                if event.key == pygame.K_3:
                    self.action_selector_change(3)
                if event.key == pygame.K_4:
                    self.action_selector_change(4)
                if event.key == pygame.K_0:
                    self.action_selector_change()
                # CAPTURE BUTTON: c key
                if event.key == pygame.K_c:
                    self.action_capture()
                # QUIT: q key
                if event.key == pygame.K_q:
                    self.running = False
            if event.type == ENCODER_ROTATED:
                self.action_rotate_encoder(event.dir)
            if event.type == CAPTURE_PRESSED:
                self.action_capture()

    def action_rotate_encoder(self, dir):
        """
        action_rotate_encoder represents one measured tick of the rotary
        encoder on the device.
        If the system isn't in gallery mode, it will switch to gallery mode.
        If it's already in gallery mode, the encoder rotation will be used to
        scrub through the available photos and videos.
        Rotating the encoder also resets any playing video files in the program
        state.
        @param dir the Direction to rotate, either FWD (clockwise) or REV.
        """
        self.last_interaction = datetime.now()
        if self.display_mode == DisplayMode.CAPTURE:
            self.display_mode = DisplayMode.GALLERY
            self.canvas = pygame.display.set_mode((640, 480), pygame.FULLSCREEN)
        else:
            # Increment or decrement current gallery position (with wrapping)
            self.nfc.gallery_scroll(dir)
            self.playing_video_file = None

    def action_capture(self):
        """
        action_capture initiates a picture or video capture on the device.
        If in picture mode, the current active camera is used to take a picture
        and then the image is saved to the filesystem.
        If in video mode, a video recording is started and system state is
        updated to indicate that a recording is active.
        Either way, a timestamp is also recorded for when the capture happened,
        so that timed events like the end of a video recording or the
        end of a picture presentation can be set up.
        """
        self.last_interaction = datetime.now()
        self.last_capture_timestamp = datetime.now()
        if self.display_mode == DisplayMode.GALLERY:
            self.display_mode = DisplayMode.CAPTURE
        else:
            if self.capture_mode == CaptureMode.PICTURE:
                print("TOOK A PICTURE!")
                # Take a pic with current self.camera

            else:
                self.recording = True
                print("STARTED A RECORDING!")
                # Take a video with current self.camera

    def action_selector_change(self, pos=None):
        """
        action_selector_change is a helper function when running the app with
        only keyboard input. It sets up an override value so that the app is
        able to switch which camera or display modes it's using even if reading
        different (or null) data from a gpio input.
        If an override is set, use the 0 key to remove it so that gpio input
        will work again.
        @param pos a SelectorPosition to use, or None.
        """
        self.last_interaction = datetime.now()
        self.pos_override = pos
    def post_custom_event(self, event_key, **attributes):
        """
        post_custom_event - a wrapper to tell pygame that a particular event
        has been triggered.
        This function is used to pass references to the pygame event bus to
        another class object, so it can trigger a specific event from its own
        code.
        @param event_key the pygame USEREVENT key to be triggered
        @param **attributes a list of named key-value attributes to include in
            the event data
        """
        my_event = pygame.event.Event(event_key, **attributes)
        pygame.event.post(my_event)

if __name__ == "__main__":
    app = CameraApp()
    app.run()
    sys.exit()
