import logging

from .commander import Commander, ControlCommandExit, SpeedMoveCommand
from .laser_pointer import XYPointer

logger = logging.getLogger('control_strategy')
logger.setLevel(logging.DEBUG)

async def filter_abs_low(value, threshold=10):
    return value if abs(value) > threshold else 0


async def rescale(value, max_value=100):
    new_val = value * value * value / (max_value * max_value)  # make curvature
    direction = 1 if value > 0 else -1
    if abs(new_val) > 0:  # monotonic gain
        new_val = new_val + 30 * direction
    return min(new_val, max_value) if direction > 0 else max(new_val, -max_value)  # cut high


class ControlStrategy:
    def __init__(self, pointer: XYPointer, commander: Commander):
        self._pointer = pointer
        self._commander = commander

    async def run(self):
        logger.debug('starting controller loop')
        async for command in self._commander.commands():
            logger.debug(f'workin on {command}')
            if isinstance(command, ControlCommandExit):
                logger.debug('commander stopping')
                await self._pointer.stop()
                return
            if isinstance(command, SpeedMoveCommand):
                h_speed = await filter_abs_low(await rescale(command.x_speed))
                v_speed = await filter_abs_low(await rescale(command.y_speed))
                logger.debug(f'speed movement: {h_speed}, {v_speed}')
                await self._pointer.move_speed(h_speed, v_speed)
