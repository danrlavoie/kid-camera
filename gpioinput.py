import logging
from functools import partial
from gpiozero import RotaryEncoder
from gpiozero import Button

from kctypes import SelectorPosition, Direction
import constants

logger = logging.getLogger(__name__)

# Used to allow the button to do both presses and holds
# https://github.com/gpiozero/gpiozero/issues/685
was_held = False

class GPIOInput():
    # This can be called to get the current value of the mode selector input
    def active_pos(self, override=None):
        """
        active_pos returns the current value of the mode selector input.
        The override argument can be used to override whatever the hardware says
        with a specific SelectorPosition value. This is useful when using keyboard
        input.
        """
        logger.debug('Function active_pos')
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

    def button_was_held(self):
        global was_held
        was_held = True
        # stuff that should happen when a hold event is triggered
        partial(self.pygame_event_fn, self.long_press_event_key)

    def button_was_pressed(self):
        # stuff that should happen on press
        partial(self.pygame_event_fn, self.capture_event_key)

    def button_was_released(self):
        global was_held
        if (not was_held):
            self.button_was_pressed()
        was_held = False

    def __init__(self, pygame_event_fn=None, encoder_event_key=None, capture_event_key=None, long_press_event_key=None):
        logger.debug('Function GPIOInput __init__')
        if (pygame_event_fn is not None):
            logger.debug('Received pygame_event_fn for passing along as a callback')
        if (encoder_event_key is not None):
            logger.debug('encoder_event_key is %s', encoder_event_key)
        if (capture_event_key is not None):
            logger.debug('capture_event_key is %s', capture_event_key)
        self.pygame_event_fn = pygame_event_fn
        self.encoder_event_key = encoder_event_key
        self.capture_event_key = capture_event_key
        self.long_press_event_key = long_press_event_key
        logger.info('Initializing GPIO inputs')
        self.encoder = RotaryEncoder(constants.ENCODER_INPUT_A_ID, constants.ENCODER_INPUT_B_ID, bounce_time=0.1, wrap=True)
        self.capture_button = Button(constants.CAPTURE_BUTTON_ID, bounce_time=0.1, hold_time=5)
        self.selector_a = Button(constants.FOURPOS_A_ID)
        self.selector_b = Button(constants.FOURPOS_B_ID)
        self.selector_c = Button(constants.FOURPOS_C_ID)
        self.selector_d = Button(constants.FOURPOS_D_ID)
        logger.info('All GPIO inputs constructed')

        self.encoder.steps = 0
        self.encoder.when_rotated_clockwise = partial(pygame_event_fn, encoder_event_key, dir=Direction.FWD)
        self.encoder.when_rotated_counter_clockwise = partial(pygame_event_fn, encoder_event_key, dir=Direction.REV)
        self.capture_button.when_held=self.button_was_held
        self.capture_button.when_released=self.button_was_released
        logger.debug('GPIO input event callbacks initialized')
if __name__ == "__main__":
    gpio = GPIOInput()
