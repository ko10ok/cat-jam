import logging

from .abstract_pin_render import PinRender


class StdOutPinsRender(PinRender):
    def __init__(self, pinout):
        self._pinout = [pin for pin in pinout]

    def __call__(self, state):
        ports_state = {self._pinout[pin]: pin_value for pin, pin_value in enumerate(state)}
        logging.getLogger().debug(f'pass to raspbery: {ports_state}')
