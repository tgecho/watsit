import os
import threading

from hardware.display import render_text

_SOUNDS_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), "sounds"))
_DEFAULT_SOUND = "chord"

DEBOUNCE_SECONDS = 0.5


class Notifier:
    def __init__(self, display, audio, leds):
        self._display = display
        self._audio = audio
        self._leds = leds
        self._display_timer = None
        self._display_lock = threading.Lock()

    def notify(self, text=None, sound=None, leds=False):
        print(f"Notifier.notify(text={text}, sound={sound}, leds={leds})")
        if text is not None:
            self._update_display(text)
        if sound is not None:
            sound_name = _DEFAULT_SOUND if sound is True else sound
            sound_file = os.path.realpath(os.path.join(_SOUNDS_DIR, f"{sound_name}.wav"))
            if not sound_file.startswith(_SOUNDS_DIR + os.sep):
                raise ValueError(f"invalid sound name: {sound!r}")
            threading.Thread(target=self._audio.play, args=(sound_file,), daemon=True).start()
        if leds:
            threading.Thread(target=self._leds.blink, daemon=True).start()

    def _update_display(self, text):
        img = render_text(text)
        with self._display_lock:
            if self._display_timer:
                self._display_timer.cancel()
            self._display_timer = threading.Timer(
                DEBOUNCE_SECONDS, self._display.show, args=(img,)
            )
            self._display_timer.start()
