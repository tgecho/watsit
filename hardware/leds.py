import time

GPIO_PIN = 18


class LEDController:
    def __init__(self):
        from gpiozero import LED
        self._led = LED(GPIO_PIN)

    def blink(self, count=3, on_ms=200, off_ms=200):
        for _ in range(count):
            self._led.on()
            time.sleep(on_ms / 1000)
            self._led.off()
            time.sleep(off_ms / 1000)


class MockLEDController:
    def blink(self):
        print("[LEDS] blink")
