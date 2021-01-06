import asyncio
import logging

# import evdev
# from gpiozero import LED
# from src import RaspberyPinsRender, GamePadController

from src import FakeController, ControlFlattener, ControlStrategy, XYPointer, PositionController, Stepper, Commander, \
    StdOutPinsRender

logging.basicConfig()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


async def main():
    #logging.getLogger('stepper_driver').setLevel(logging.INFO)
    #logging.getLogger('gamepad').setLevel(logging.INFO)
    #logging.getLogger('laser_pointer').setLevel(logging.INFO)
    #logging.getLogger('commander').setLevel(logging.INFO)
    #logging.getLogger('control_strategy').setLevel(logging.INFO)

    s1 = PositionController(Stepper(StdOutPinsRender([1, 2, 3, 4])))
    s2 = PositionController(Stepper(StdOutPinsRender([1, 2, 3, 4])))
    # s1 = PositionController(Stepper(RaspberyPinsRender([LED(12), LED(16), LED(20), LED(21)])))
    # s2 = PositionController(Stepper(RaspberyPinsRender([LED(6), LED(13), LED(19), LED(26)])))

    # device = evdev.list_devices()[0]
    # logging.getLogger().debug(f'device {device}')

    c = ControlStrategy(
        XYPointer(s1, s2),
        Commander(FakeController('any_path'), ControlFlattener())
        # Commander(GamePadController(device), ControlFlattener())
    )

    await asyncio.gather(
        s1.run(),
        s2.run(),
        c.run(),
    )


if __name__ == '__main__':
    asyncio.run(main())
