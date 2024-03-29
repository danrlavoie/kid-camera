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
        pass
        # if self.selector_a.is_pressed:
            # return SelectorPosition.ONE
        # if self.selector_b.is_pressed:
            # return SelectorPosition.TWO
        # if self.selector_c.is_pressed:
            # return SelectorPosition.THREE
        # if self.selector_d.is_pressed:
            # return SelectorPosition.FOUR

    def __init__(self, encoder_fn=None, capture_fn=None):
        load_dotenv()
        env = os.environ
        self.encoder_steps = 0
        print("HI")
        # Attach callbacks if keyboard input is active
        if (env['USE_KEYBOARD_INPUT']):
            if (encoder_fn):
                self.setup_encoder_callback(encoder_fn)
            if (capture_fn):
                self.setup_capture_callback(capture_fn)


