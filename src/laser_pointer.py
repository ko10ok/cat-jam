import logging
from collections import namedtuple

from .stepper_driver import PositionController

logger = logging.getLogger('laser_pointer')
logger.setLevel(logging.DEBUG)

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
