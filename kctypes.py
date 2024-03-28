from enum import Enum

class Camera(Enum):
    SELFIE = 1
    FORWARD = 2

class CaptureMode(Enum):
    PICTURE = 1
    VIDEO = 2

class DisplayMode(Enum):
    GALLERY = 1
    CAPTURE = 2

class SelectorPosition(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4

class Direction(Enum):
    FWD = 1
    REV = 2
