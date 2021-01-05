import evdev


class GamePadController:
    def __init__(self, path):
        self._controller: evdev.InputDevice = evdev.InputDevice(path)

    async def events(self):
        async for event in self._controller.async_read_loop():
            yield event
