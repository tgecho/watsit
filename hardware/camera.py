import io

from PIL import Image, ImageDraw


class Camera:
    def __init__(self):
        from picamera2 import Picamera2
        self._cam = Picamera2()
        self._cam.configure(self._cam.create_still_configuration())
        self._cam.start()

    def capture(self) -> bytes:
        buf = io.BytesIO()
        self._cam.capture_file(buf, format="jpeg")
        buf.seek(0)
        return buf.read()


class MockCamera:
    def capture(self) -> bytes:
        img = Image.new("RGB", (640, 480), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        draw.text((240, 220), "MOCK CAMERA", fill=(180, 180, 180))
        buf = io.BytesIO()
        img.save(buf, format="jpeg")
        buf.seek(0)
        return buf.read()
