import logging
from asyncio import sleep
from itertools import cycle
from time import time

logger = logging.getLogger('fake_gamepad')
logger.setLevel(logging.DEBUG)


class FakeInputEvent:
    def __init__(self, code, type, value, sec=None, usec=None):
        self.code = code
        self.type = type
        self.value = value
        timestamp = time()
        self.sec = sec if sec else int(timestamp)
        self.usec = usec if usec else int(timestamp % 1 * 1000_000)

    def timestamp(self):
        return self.sec + (self.usec / 1000_000)

    def __repr__(self):
        return f'FakeInputEvent({self.code}, {self.type}, {self.value}, {self.sec}, {self.usec})'

    def __str__(self):
        return f'FakeInputEvent(code={self.code}, type={self.type}, value={self.value}, sec={self.sec}, usec={self.usec})'


class FakeCommand:
    def __call__(self):
        raise NotImplementedError


class FakeSleepCommand(FakeCommand):
    def __init__(self, time):
        self._time = time

    async def __call__(self):
        logger.debug('sleepeng')
        await sleep(self._time)


class FakeController:
    def __init__(self, path):
        logger.debug(f'path={path}')
        pass

    async def events(self):
        for event in cycle([
            FakeInputEvent(308, 1, 1),
            FakeSleepCommand(1),
            FakeInputEvent(308, 1, 0),
            FakeSleepCommand(1),
            FakeInputEvent(304, 1, 1),
            FakeSleepCommand(1),
            FakeInputEvent(304, 1, 0),
            FakeSleepCommand(1),

            FakeInputEvent(307, 1, 1),
            FakeSleepCommand(1),
            FakeInputEvent(307, 1, 0),
            FakeSleepCommand(1),
            FakeInputEvent(305, 1, 1),
            FakeSleepCommand(1),
            FakeInputEvent(305, 1, 0),
            FakeSleepCommand(1),

            FakeInputEvent(290, 3, -100),
            FakeInputEvent(290, 4, -100),
            FakeInputEvent(290, 1, 1),
            FakeSleepCommand(1),
            FakeInputEvent(290, 3, 1000),
            FakeInputEvent(290, 4, 1000),
            FakeInputEvent(290, 1, 1),
            FakeSleepCommand(1),
            FakeInputEvent(290, 1, 0),
            FakeInputEvent(290, 3, -3000),
            FakeInputEvent(290, 4, -3000),
            FakeSleepCommand(1),

            FakeInputEvent(315, 1, 1),
        ]):
            yield event
