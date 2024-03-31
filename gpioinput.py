from functools import partial
from gpiozero import RotaryEncoder
from gpiozero import Button
from dotenv import load_dotenv
import os

from kctypes import SelectorPosition, Direction
class GPIOInput():
    # This can be called to get the current value of the mode selector input
    def active_pos(self, override=None):
        """
        active_pos returns the current value of the mode selector input.
        The override argument can be used to override whatever the hardware says
        with a specific SelectorPosition value. This is useful when using keyboard
        input.
        """
        if (override != None):
            return override
        if self.selector_a.is_pressed:
            return SelectorPosition.ONE
        if self.selector_b.is_pressed:
            return SelectorPosition.TWO
        if self.selector_c.is_pressed:
            return SelectorPosition.THREE
        if self.selector_d.is_pressed:
            return SelectorPosition.FOUR

    def __init__(self, pygame_event_fn=None, encoder_event_key=None, capture_event_key=None ):
        load_dotenv()
        env = os.environ
        self.pygame_event_fn = pygame_event_fn
        self.encoder_event_key = encoder_event_key
        self.capture_event_key = capture_event_key
        self.encoder = RotaryEncoder(env['ENCODER_INPUT_A_ID'], env['ENCODER_INPUT_B_ID'], bounce_time=0.2, wrap=True)
        self.capture_button = Button(env['CAPTURE_BUTTON_ID'], bounce_time=0.2)
        self.selector_a = Button(env['FOURPOS_A_ID'])
        self.selector_b = Button(env['FOURPOS_B_ID'])
        self.selector_c = Button(env['FOURPOS_C_ID'])
        self.selector_d = Button(env['FOURPOS_D_ID'])

        self.encoder.steps = 0
        self.encoder.when_rotated_clockwise = partial(pygame_event_fn, encoder_event_key, dir=Direction.FWD)
        self.encoder.when_rotated_counter_clockwise = partial(pygame_event_fn, encoder_event_key, dir=Direction.REV)
        self.capture_button.when_pressed = partial(pygame_event_fn, capture_event_key)
if __name__ == "__main__":
    gpio = GPIOInput()
