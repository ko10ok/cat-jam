from .abstract_pin_render import PinRender


class RaspberyPinsRender(PinRender):
    def __init__(self, pinout):
        self._pinout = [pin for pin in pinout]

    def __call__(self, state):
        for idx, pin in enumerate(self._pinout):
            pin.on() if state[idx] else pin.off()
