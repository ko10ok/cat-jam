from pip._internal.utils import logging

from .commander import Commander, ControlCommandExit, SpeedMoveCommand
from .laser_pointer import XYPointer


class ControlStrategy:
    def __init__(self, pointer: XYPointer, commander: Commander):
        self._pointer = pointer
        self._commander = commander
        self._events = []

    async def run(self):
        logging.getLogger().debug('starting controller loop')
        async for command in self._commander.commands():
            logging.getLogger().debug(f'workin on {command}')
            if isinstance(command, ControlCommandExit):
                logging.getLogger().debug('commander stopping')
                await self._pointer.stop()
                return
            if isinstance(command, SpeedMoveCommand):
                h_speed, v_speed = command
                logging.getLogger().debug(f'speed movement: {h_speed}, {v_speed}')
                await self._pointer.move_speed(h_speed, v_speed)
