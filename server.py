import os

from flask import Flask, request, jsonify, Response

from hardware.display import EinkDisplay, MockDisplay
from hardware.audio import AudioPlayer, MockAudioPlayer
from hardware.leds import LEDController, MockLEDController
from hardware.camera import Camera, MockCamera
from notifier import Notifier

app = Flask(__name__)

MOCK = os.environ.get("MOCK_HARDWARE", "1") == "1"

display = MockDisplay() if MOCK else EinkDisplay()
audio = MockAudioPlayer() if MOCK else AudioPlayer()
leds = MockLEDController()# if MOCK else LEDController()
camera = MockCamera() #if MOCK else Camera()

notifier = Notifier(display, audio, leds)


@app.route("/notify", methods=["POST"])
def notify():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "invalid JSON"}), 400

    notifier.notify(
        text=data.get("text"),
        sound=data.get("sound"),
        leds=data.get("leds", False),
    )
    return jsonify({"ok": True})


@app.route("/snapshot")
def snapshot():
    return Response(camera.capture(), mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=MOCK)
