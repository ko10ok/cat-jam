import logging

import evdev

logger = logging.getLogger('gamepad')
logger.setLevel(logging.DEBUG)


class GamePadController:
    def __init__(self, path):
        self._controller: evdev.InputDevice = evdev.InputDevice(path)
        logger.debug(f'gamepad: {self._controller}')

    async def events(self):
        async for event in self._controller.async_read_loop():
            logger.debug(f'incoming event: code={event.code}, type={event.type}, value={event.value}')
            yield event
