import asyncio
import logging

# import evdev
# from gpiozero import LED

from src import FakeController, ControlFlattener, ControlStrategy, XYPointer, PositionController, Stepper, Commander, \
    StdOutPinsRender, RaspberyPinsRender

logging.basicConfig()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


async def main():
    s1 = PositionController(Stepper(StdOutPinsRender([1, 2, 3, 4])))
    s2 = PositionController(Stepper(StdOutPinsRender([1, 2, 3, 4])))
    # s1 = PositionController(Stepper(RaspberyPinsRender([LED(12), LED(16), LED(20), LED(21)])))
    # s2 = PositionController(Stepper(RaspberyPinsRender([LED(6), LED(13), LED(19), LED(26)])))

    c = ControlStrategy(
        XYPointer(s1, s2),
        Commander(FakeController('any_path'), ControlFlattener())
        # Commander(GamePadController(evdev.list_devices()[0]), ControlFlattener())
    )

    await asyncio.gather(
        s1.run(),
        s2.run(),
        c.run(),
    )


if __name__ == '__main__':
    asyncio.run(main())
