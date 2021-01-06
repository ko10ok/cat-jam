import logging

from .abstract_pin_render import PinRender

logger = logging.getLogger('std_out_pin_render')
logger.setLevel(logging.DEBUG)

class StdOutPinsRender(PinRender):
    def __init__(self, pinout):
        self._pinout = [pin for pin in pinout]

    def __call__(self, state):
        ports_state = {self._pinout[pin]: pin_value for pin, pin_value in enumerate(state)}
        logger.debug(f'pass to raspbery: {ports_state}')
