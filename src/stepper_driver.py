import logging
from asyncio import sleep

from .pin_render.abstract_pin_render import PinRender

logger = logging.getLogger('stepper_driver')
logger.setLevel(logging.WARN)


class Stepper:
    def __init__(self, render: PinRender):
        self._render = render
        self._state = [1, 1, 0, 0]

    async def rshift(self):
        self._state.append(self._state.pop(0))
        self._render(self._state)

    async def lshift(self):
        self._state.insert(0, self._state.pop())
        self._render(self._state)

    async def step(self, direction_speed):
        """
        :param direction_speed: -100 : 100
        """

        async def arange(range_count):
            for i in range(range_count):
                yield i

        speed_delay = 0.100 - abs(direction_speed) / 1_000
        logger.debug(f'delay for step rate: {speed_delay}')
        if direction_speed > 0:
            await self.rshift()
            await sleep(0.002 + speed_delay)
        if direction_speed < 0:
            await self.lshift()
            await sleep(0.002 + speed_delay)


class PositionController:
    def __init__(self, motor: Stepper):
        self._motor = motor
        self._position = 0
        self._target_position = None
        self._delta = 0
        self._stop = None
        # run thread for loading motors

    async def move_speed(self, speed):
        # TODO steps from speed coeficient
        self._delta = speed

    async def move_to_position(self, position):
        self._delta = 0
        self._target_position = position

    @property
    async def position(self):
        return self._position

    async def reset_position(self):
        self._position = 0

    async def stop(self):
        logger.debug(f'getting stop signal on {self._stop}')
        self._stop = True

    async def run(self):
        logger.debug(f'run on {self._motor}')
        while not self._stop:
            # logger.debug(f'params: motor={self._motor} pos={self._position} tpos={self._target_position} delta={self._delta}, stop={self._stop}')
            if self._target_position:
                # move to target
                self._target_position = None
            else:
                # logger.debug(f'running delta: {self._delta}')
                await self._motor.step(self._delta)
            await sleep(0)
        logger.debug(f'stopped {self._stop}')
