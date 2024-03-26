from enum import Enum
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

class Camera(Enum):
    SELFIE = 1
    FORWARD = 2

class CaptureMode(Enum):
    PICTURE = 1
    VIDEO = 2

class CameraApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit program")
    ]
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
    def action_toggle_dark(self) -> None:
        self.dark = not self.dark
    def action_quit(self) -> None:
        exit()
if __name__ == "__main__":
    app = CameraApp()
    app.run()
