from asyncio import sleep
from collections import namedtuple

from pip._internal.utils import logging

from .pin_render.abstract_pin_render import PinRender


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
        if direction_speed > 0:
            await self.rshift()
        if direction_speed < 0:
            await self.lshift()
        # min driver resolution delay
        await sleep(0.1)


# class LogThrottling:
#     def __init__(self, delay = None , times = None):
#         self._delay = delay
#         self._times = times
#
#     def __call__(self, *args, **kwargs):
#

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
        logging.getLogger().debug(f'getting stop signal on {self._stop}')
        self._stop = True

    async def run(self):
        logging.getLogger().debug(f'run on {self._motor}')
        while not self._stop:
            logging.getLogger().debug(f'params: motor={self._motor} pos={self._position} tpos={self._target_position} delta={self._delta}, stop={self._stop}')
            if self._target_position:
                # move to target
                self._target_position = None
            else:
                for i in range(abs(self._delta)):
                    logging.getLogger().debug(f'running delta: {self._delta}')
                    await self._motor.step(self._delta)
            await sleep(0.1)
        logging.getLogger().debug(f'stopped {self._stop}')

Point = namedtuple('Point', ['x', 'y'])


class XYPointer:
    def __init__(self, vert: PositionController, horizont: PositionController):
        self._vert = vert
        self._horizont = horizont

    async def move_speed(self, vert_speed, horizont_speed):
        # TODO do not apply as is
        # add angle  correction
        await self._vert.move_speed(vert_speed)
        await self._horizont.move_speed(horizont_speed)

    async def pick_point(self):
        return Point(self._vert.position, self._horizont.position)

    async def move_to(self, point: Point):
        await self._vert.move_to_position(point.y)
        await self._horizont.move_to_position(point.y)

    async def stop(self):
        await self._vert.stop()
        await self._horizont.stop()
