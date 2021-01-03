import evdev
from evdev import ecodes

from gpiozero import LED


class Render:
    def __init__(self, pinout):
        self._pinout = [pin for pin in pinout]

    def __call__(self, state):
        for idx, pin in enumerate(self._pinout):
            pin.on() if state[idx] else pin.off()


class Stepper:
    def __init__(self, render):
        self._render = render
        self._state = [1, 1, 0, 0]

    def rshift(self):
        self._state.append(self._state.pop(0))
        self._render(self._state)

    def lshift(self):
        self._state.insert(0, self._state.pop())
        self._render(self._state)


if __name__ == '__main__':

    print(f'{evdev.list_devices()=}')
    controller = evdev.InputDevice(evdev.list_devices()[0])

    s1 = Stepper(Render([LED(12), LED(16), LED(20), LED(21)]))
    s2 = Stepper(Render([LED(6), LED(13), LED(19), LED(26)]))

    for event in controller.read_loop():
        print(f'{event=}')
        print(f'{event.code=}, {event.type=}, {event.value=}')
        if event.code == 308 and event.type == 1 and event.value == 1:
            s1.rshift()
        elif event.code == 304 and event.type == 1 and event.value == 1:
            s1.lshift()

        if event.code == 307 and event.type == 1 and event.value == 1:
            s2.rshift()
        elif event.code == 305 and event.type == 1 and event.value == 1:
            s2.lshift()
