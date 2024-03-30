from dotenv import load_dotenv
import os

from kctypes import SelectorPosition
class KeyboardInput():
    # This sets up a function to be called when the encoder is rotated
    # TODO: Might need to wrap the current rotation amount and pass it to fn
    def setup_encoder_callback(self, fn):
        pass

    # This sets up a function to be called when the capture button is pressed
    def setup_capture_callback(self, fn):
        pass

    # This can be called to get the current value of the mode selector input
    def active_pos(self):
        if self._pos == 1:
            return SelectorPosition.ONE
        elif self._pos == 2:
            return SelectorPosition.TWO
        elif self._pos == 3:
            return SelectorPosition.THREE
        elif self._pos == 4:
            return SelectorPosition.FOUR

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self, value):
        self._pos = value
    def __init__(self, encoder_fn=None, capture_fn=None):
        load_dotenv()
        env = os.environ
        self._pos = 1
        self.encoder_steps = 0
        print("HI")
        # Attach callbacks if keyboard input is active
        if (env['USE_KEYBOARD_INPUT']):
            if (encoder_fn):
                self.setup_encoder_callback(encoder_fn)
            if (capture_fn):
                self.setup_capture_callback(capture_fn)


