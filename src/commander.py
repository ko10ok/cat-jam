import logging
from collections import namedtuple

from .controller.fake_gamepad import FakeCommand

logger = logging.getLogger('commander')
logger.setLevel(logging.DEBUG)

SpeedMoveCommand = namedtuple('SpeedMoveCommand', ['x_speed', 'y_speed'])


class ControlCommandExit:
    pass


async def abs_max(value, max_value):
    if value >= 0:
        return min(value, max_value)
    else:
        return max(value, -max_value)

async def speeds_command(events) -> SpeedMoveCommand:
    # FAKE implementation
    # TODO realization of pointer speed logic with
    # commander cant do pure speed, hust controller speed.
    # if control is active
    # and last value set
    # set corresponding speed param
    v_speed, h_speed = 0, 0

    up_event = events.get(308, None)
    down_event = events.get(304, None)
    if up_event and (up_event.type == 1 and up_event.value == 1):
        v_speed = 100
    elif down_event and (down_event.type == 1 and down_event.value == 1):
        v_speed = -100
    else:
        v_speed = 0
    if up_event and down_event:
        # both selected case skipped
        v_speed = 0

    left_event = events.get(307, None)
    right_event = events.get(305, None)

    if left_event and (left_event.type == 1 and left_event.value == 1):
        h_speed = 100
    elif right_event and (right_event.type == 1 and right_event.value == 1):
        h_speed = -100
    else:
        h_speed = 0
    if left_event and right_event:
        # both selected case skipped
        h_speed = 0

    # panel_event = events.get(290, None)
    # v_panel_value = events.get(3, None)
    # h_panel_value = events.get(4, None)
    # if panel_event and panel_event.type == 1 and panel_event.value == 1 and v_panel_value and v_panel_value.type == 3:
    #     v_speed = v_panel_value.value / (2 ** 15 - 1) * 100
    # if panel_event and panel_event.type == 1 and panel_event.value == 1 and h_panel_value and h_panel_value.type == 3:
    #     h_speed = h_panel_value.value / (2 ** 15 - 1) * 100
    # if panel_event and panel_event.type == 1 and panel_event.type == 0:
    #     v_speed = 0
    #     h_speed = 0

    v_joystick = events.get(0, None)
    h_joystick = events.get(1, None)
    if v_joystick and v_joystick.type == 3:
        v_speed = await abs_max(v_joystick.value, 21_000) / (21_000) * 100
    if h_joystick and h_joystick.type == 3:
        h_speed = await abs_max(h_joystick.value, 21_000) / (21_000) * 100

    return SpeedMoveCommand(h_speed, v_speed)


async def filter_zeroes(event):
    if event.code == 0 and event.type == 0 and event.value == 0:
        return {None: None}
    return {event.code: event}


class ControlFlattener:
    def __init__(self):
        self.events = {}

    async def cleanup_not_pressed(self):
        if 290 in self.events and self.events[290].type == 1 and self.events[290].value == 0:
            if 3 in self.events:
                self.events.pop(3)
            if 4 in self.events:
                self.events.pop(4)

        self.events = {
            key: event
            for key, event in self.events.items()
            if not ((
                            key in [308, 307, 305, 304]
                            and event.type == 1 and event.value == 0
                    ) or (
                            key in [290, 289]
                            and event.type == 1 and event.value == 0
                    ))
        }

        logger.debug(f'cleaned up events: {self.events}')

    async def __call__(self, event):
        self.events.update(await filter_zeroes(event))
        logger.debug(f'result events: {self.events}')
        return self.events


class Commander:
    def __init__(self, controller, events_flattener):
        self._controller = controller
        self._events_flattener = events_flattener
        # {control_id: event}

    async def commands(self):
        async for event in self._controller.events():
            logger.debug(f'controller event={event}')
            if isinstance(event, FakeCommand):
                await event()
                continue

            logger.debug(f'fake event: {event}')
            if event.code == 315 and event.type == 1 and event.value == 1:
                yield ControlCommandExit()
                return

            events = await self._events_flattener(event)
            yield await speeds_command(events)
            await self._events_flattener.cleanup_not_pressed()

# log of finger 1-session
#
# l_panel
# DEBUG:root:controller event=event at 1609838408.445151, code 16, type 03, val -22954
# DEBUG:root:controller event=event at 1609838408.445151, code 17, type 03, val -5002
# DEBUG:root:controller event=event at 1609838408.445151, code 289, type 01, val 01
# DEBUG:root:controller event=event at 1609838408.445151, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838408.453165, code 16, type 03, val -23546
# DEBUG:root:controller event=event at 1609838408.453165, code 17, type 03, val -4855
# DEBUG:root:controller event=event at 1609838408.453165, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838408.461173, code 17, type 03, val -4891
# DEBUG:root:controller event=event at 1609838408.461173, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838408.473126, code 16, type 03, val -23513
# DEBUG:root:controller event=event at 1609838408.473126, code 17, type 03, val -5788
# DEBUG:root:controller event=event at 1609838408.473126, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838408.481140, code 16, type 03, val 00
# DEBUG:root:controller event=event at 1609838408.481140, code 17, type 03, val 00
# DEBUG:root:controller event=event at 1609838408.481140, code 289, type 01, val 00
# DEBUG:root:controller event=event at 1609838408.481140, code 00, type 00, val 00
#
#
# y-a
# DEBUG:root:controller event=event at 1609838444.749019, code 304, type 01, val 01
# DEBUG:root:controller event=event at 1609838444.749019, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838445.552998, code 308, type 01, val 01
# DEBUG:root:controller event=event at 1609838445.552998, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838446.332991, code 304, type 01, val 00
# DEBUG:root:controller event=event at 1609838446.332991, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838447.152989, code 308, type 01, val 00
# DEBUG:root:controller event=event at 1609838447.152989, code 00, type 00, val 00
#
#
# r-panel
# DEBUG:root:controller event=event at 1609838450.620982, code 03, type 03, val -57
# DEBUG:root:controller event=event at 1609838450.620982, code 04, type 03, val -8436
# DEBUG:root:controller event=event at 1609838450.620982, code 290, type 01, val 01
# DEBUG:root:controller event=event at 1609838450.620982, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.628991, code 03, type 03, val -18
# DEBUG:root:controller event=event at 1609838450.628991, code 04, type 03, val -8289
# DEBUG:root:controller event=event at 1609838450.628991, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.640939, code 04, type 03, val -7062
# DEBUG:root:controller event=event at 1609838450.640939, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.645078, code 03, type 03, val 27
# DEBUG:root:controller event=event at 1609838450.645078, code 04, type 03, val -7013
# DEBUG:root:controller event=event at 1609838450.645078, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.656990, code 03, type 03, val 194
# DEBUG:root:controller event=event at 1609838450.656990, code 04, type 03, val -6278
# DEBUG:root:controller event=event at 1609838450.656990, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.664968, code 03, type 03, val 756
# DEBUG:root:controller event=event at 1609838450.664968, code 04, type 03, val -5690
# DEBUG:root:controller event=event at 1609838450.664968, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.672961, code 03, type 03, val 1546
# DEBUG:root:controller event=event at 1609838450.672961, code 04, type 03, val -4316
# DEBUG:root:controller event=event at 1609838450.672961, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.680953, code 03, type 03, val 3062
# DEBUG:root:controller event=event at 1609838450.680953, code 04, type 03, val -2942
# DEBUG:root:controller event=event at 1609838450.680953, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.692955, code 03, type 03, val 4642
# DEBUG:root:controller event=event at 1609838450.692955, code 04, type 03, val -1470
# DEBUG:root:controller event=event at 1609838450.692955, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.700965, code 03, type 03, val 6158
# DEBUG:root:controller event=event at 1609838450.700965, code 04, type 03, val -588
# DEBUG:root:controller event=event at 1609838450.700965, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.708967, code 03, type 03, val 7278
# DEBUG:root:controller event=event at 1609838450.708967, code 04, type 03, val 98
# DEBUG:root:controller event=event at 1609838450.708967, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.716974, code 03, type 03, val 8396
# DEBUG:root:controller event=event at 1609838450.716974, code 04, type 03, val 1176
# DEBUG:root:controller event=event at 1609838450.716974, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.728958, code 03, type 03, val 8924
# DEBUG:root:controller event=event at 1609838450.728958, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.736975, code 04, type 03, val 980
# DEBUG:root:controller event=event at 1609838450.736975, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.744976, code 04, type 03, val 931
# DEBUG:root:controller event=event at 1609838450.744976, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.752970, code 03, type 03, val 8726
# DEBUG:root:controller event=event at 1609838450.752970, code 04, type 03, val 294
# DEBUG:root:controller event=event at 1609838450.752970, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.760949, code 03, type 03, val 00
# DEBUG:root:controller event=event at 1609838450.760949, code 04, type 03, val 147
# DEBUG:root:controller event=event at 1609838450.760949, code 290, type 01, val 00
# DEBUG:root:controller event=event at 1609838450.760949, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609838450.772955, code 04, type 03, val 110
# DEBUG:root:controller event=event at 1609838450.772955, code 00, type 00, val 00
#
# r-l
# DEBUG:root:controller event=event at 1609839442.744868, code 307, type 01, val 01
# DEBUG:root:controller event=event at 1609839442.744868, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839443.248853, code 305, type 01, val 01
# DEBUG:root:controller event=event at 1609839443.248853, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839443.916846, code 307, type 01, val 00
# DEBUG:root:controller event=event at 1609839443.916846, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839444.480847, code 305, type 01, val 00
# DEBUG:root:controller event=event at 1609839444.480847, code 00, type 00, val 00
#


# joystick
#
#
# DEBUG:root:controller event=event at 1609839576.020545, code 00, type 03, val 4083
# DEBUG:root:controller event=event at 1609839576.020545, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839576.056276, code 00, type 03, val 3937
# DEBUG:root:controller event=event at 1609839576.056276, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839576.068301, code 00, type 03, val 1444
# DEBUG:root:controller event=event at 1609839576.068301, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839576.076293, code 00, type 03, val 00
# DEBUG:root:controller event=event at 1609839576.076293, code 00, type 00, val 00
#
#
# DEBUG:root:controller event=event at 1609839584.708386, code 00, type 03, val -12951
# DEBUG:root:controller event=event at 1609839584.708386, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839584.716275, code 00, type 03, val -15383
# DEBUG:root:controller event=event at 1609839584.716275, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839584.724281, code 00, type 03, val -18271
# DEBUG:root:controller event=event at 1609839584.724281, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839584.732238, code 00, type 03, val -19639
# DEBUG:root:controller event=event at 1609839584.732238, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839584.744235, code 00, type 03, val -20248
# DEBUG:root:controller event=event at 1609839584.744235, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839584.752254, code 00, type 03, val -20400
# DEBUG:root:controller event=event at 1609839584.752254, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839584.760262, code 00, type 03, val -20248
# DEBUG:root:controller event=event at 1609839584.760262, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839584.768235, code 00, type 03, val -18424
# DEBUG:root:controller event=event at 1609839584.768235, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839584.780233, code 00, type 03, val 2069
# DEBUG:root:controller event=event at 1609839584.780233, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839584.788246, code 00, type 03, val 00
# DEBUG:root:controller event=event at 1609839584.788246, code 00, type 00, val 00
#
# DEBUG:root:controller event=event at 1609839588.776251, code 00, type 03, val -100
# DEBUG:root:controller event=event at 1609839588.776251, code 01, type 03, val -82
# DEBUG:root:controller event=event at 1609839588.776251, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839588.784255, code 00, type 03, val -186
# DEBUG:root:controller event=event at 1609839588.784255, code 01, type 03, val -148
# DEBUG:root:controller event=event at 1609839588.784255, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839588.792206, code 00, type 03, val -86
# DEBUG:root:controller event=event at 1609839588.792206, code 01, type 03, val -65
# DEBUG:root:controller event=event at 1609839588.792206, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839588.800207, code 00, type 03, val -186
# DEBUG:root:controller event=event at 1609839588.800207, code 01, type 03, val -148
# DEBUG:root:controller event=event at 1609839588.800207, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839588.812220, code 00, type 03, val -100
# DEBUG:root:controller event=event at 1609839588.812220, code 01, type 03, val -82
# DEBUG:root:controller event=event at 1609839588.812220, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839588.820256, code 00, type 03, val -17
# DEBUG:root:controller event=event at 1609839588.820256, code 01, type 03, val -14
# DEBUG:root:controller event=event at 1609839588.820256, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839588.848209, code 00, type 03, val 00
# DEBUG:root:controller event=event at 1609839588.848209, code 01, type 03, val 00
# DEBUG:root:controller event=event at 1609839588.848209, code 00, type 00, val 00
#
#
# DEBUG:root:controller event=event at 1609839592.240234, code 00, type 03, val 326
# DEBUG:root:controller event=event at 1609839592.240234, code 01, type 03, val 658
# DEBUG:root:controller event=event at 1609839592.240234, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839592.248244, code 00, type 03, val 6836
# DEBUG:root:controller event=event at 1609839592.248244, code 01, type 03, val 13063
# DEBUG:root:controller event=event at 1609839592.248244, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839592.256177, code 00, type 03, val 15724
# DEBUG:root:controller event=event at 1609839592.256177, code 01, type 03, val 28619
# DEBUG:root:controller event=event at 1609839592.256177, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839592.268176, code 00, type 03, val 19750
# DEBUG:root:controller event=event at 1609839592.268176, code 01, type 03, val 32767
# DEBUG:root:controller event=event at 1609839592.268176, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839592.276238, code 00, type 03, val 20243
# DEBUG:root:controller event=event at 1609839592.276238, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839592.304212, code 00, type 03, val 19498
# DEBUG:root:controller event=event at 1609839592.304212, code 00, type 00, val 00
# DEBUG:root:controller event=event at 1609839592.312219, code 00, type 03, val 00
# DEBUG:root:controller event=event at 1609839592.312219, code 01, type 03, val 00
# DEBUG:root:controller event=event at 1609839592.312219, code 00, type 00, val 00
#
