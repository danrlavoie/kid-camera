from gpiozero import RotaryEncoder
from gpiozero import Button
from dotenv import load_dotenv

class FourPosition(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
class GPIOInput():
    def active_pos(self):
        if self.four_pos_a.is_pressed:
            return FourPosition.ONE
        if self.four_pos_b.is_pressed:
            return FourPosition.TWO
        if self.four_pos_c.is_pressed:
            return FourPosition.THREE
        if self.four_pos_d.is_pressed:
            return FourPosition.FOUR
    def __init__(self):
        load_dotenv()
        env = os.environ
        self.encoder = RotaryEncoder(env['ENCODER_INPUT_A_ID'], env['ENCODER_INPUT_B_ID'], wrap=True)
        self.capture_button = Button(env['CAPTURE_BUTTON_ID'])
        self.four_pos_a = Button(env['FOURPOS_A_ID'])
        self.four_pos_b = Button(env['FOURPOS_B_ID'])
        self.four_pos_c = Button(env['FOURPOS_C_ID'])
        self.four_pos_d = Button(env['FOURPOS_D_ID'])

        self.encoder.steps = 0
        self.encoder.when_rotated = exit()

        self.capture_button.when_pressed = exit()
if __name__ == "__main__":
    gpio = GPIOInput()
