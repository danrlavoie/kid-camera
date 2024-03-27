from enum import Enum
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from datetime import datetime, timedelta
# libcamera, libcamera-vid

from nfc import NFC
from album import Album

class Camera(Enum):
    SELFIE = 1
    FORWARD = 2

class CaptureMode(Enum):
    PICTURE = 1
    VIDEO = 2

class DisplayMode(Enum):
    GALLERY = 1
    CAPTURE = 2

class CameraApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("c", "capture", "Capture button pressed"),
        ("n", "toggle_nfc", "Toggle NFC activation"),
        ("r", "rotate_encoder", "Encoder rotated"),
        ("q", "quit", "Quit program")
    ]
    def __init__(self):
        super().__init__(self)
        self.dark = False
        self.camera = Camera.SELFIE
        self.capture_mode = CaptureMode.PICTURE
        self.display_mode = DisplayMode.GALLERY
        # The timestamp at which the last image was taken
        self.last_capture_timestamp = datetime.min
        # The timestamp at which the last button press occurred
        self.last_interaction = datetime.now
        # A timeout of how long to show an image/gif after it finishes
        self.presentation_timeout = timedelta(seconds = 5)
        # ID of current NFC card - if None, is not interfacing with a card
        # NFC card just maintains its ID
        # Store the last position for each album or else use 0
        self.active_nfc_id = None
        self.nfc = NFC()
        self.album = Album(self.nfc.pic_path)
        # The current timestamp
        # Consider limiting the total size of the album files
        # Videos and images interspersed by timestamp
        # Videos should loop after finishing
    def activate_nfc(self, nfc_id):
        self.active_nfc_id = nfc_id
    def deactivate_nfc(self):
        self.active_nfc_id = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_rotate_encoder(self) -> None:
        if self.display_mode == DisplayMode.CAPTURE:
            self.display_mode = DisplayMode.GALLERY
        else:
            # Increment or decrement current album position (with wrapping)
    def action_capture(self) -> None:
        if self.display_mode == DisplayMode.GALLERY:
            self.display_mode = DisplayMode.CAPTURE
        else:
            if self.capture_mode == CaptureMode.PICTURE:
                # Take a pic with current self.camera
            else:
                # Take a video with current self.camera
            # Then, set last_capture_timestamp to now
            self.last_capture_timestamp = datetime.now()
        # Finally, set last_interaction to now
        self.last_interaction = datetime.now()
    def action_quit(self) -> None:
        exit()

if __name__ == "__main__":
    app = CameraApp()
    app.run()
