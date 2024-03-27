from gpiozero import RotaryEncoder
from gpiozero import Button
from dotenv import load_dotenv
import os

from kctypes import SelectorPosition
class GPIOInput():
    # This sets up a function to be called when the encoder is rotated
    # TODO: Might need to wrap the current rotation amount and pass it to fn
    def setup_encoder_callback(self, fn):
        self.encoder.when_rotated = fn

    # This sets up a function to be called when the capture button is pressed
    def setup_capture_callback(self, fn):
        self.capture_button.when_pressed = fn

    # This can be called to get the current value of the mode selector input
    def active_pos(self):
        if self.selector_a.is_pressed:
            return SelectorPosition.ONE
        if self.selector_b.is_pressed:
            return SelectorPosition.TWO
        if self.selector_c.is_pressed:
            return SelectorPosition.THREE
        if self.selector_d.is_pressed:
            return SelectorPosition.FOUR

    def __init__(self, encoder_fn=None, capture_fn=None):
        load_dotenv()
        env = os.environ
        self.encoder = RotaryEncoder(env['ENCODER_INPUT_A_ID'], env['ENCODER_INPUT_B_ID'], wrap=True)
        self.capture_button = Button(env['CAPTURE_BUTTON_ID'])
        self.selector_a = Button(env['FOURPOS_A_ID'])
        self.selector_b = Button(env['FOURPOS_B_ID'])
        self.selector_c = Button(env['FOURPOS_C_ID'])
        self.selector_d = Button(env['FOURPOS_D_ID'])

        self.encoder.steps = 0

        if (encoder_fn):
            self.setup_encoder_callback(encoder_fn)
        if (capture_fn):
            self.setup_capture_callback(capture_fn)

if __name__ == "__main__":
    gpio = GPIOInput()
