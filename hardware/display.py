from PIL import Image, ImageDraw, ImageFont

DISPLAY_W = 250
DISPLAY_H = 122

_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Raspberry Pi OS / Debian
    "/System/Library/Fonts/Helvetica.ttc",              # macOS
]


def _load_font(size):
    for path in _FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            pass
    return ImageFont.load_default()


def _wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width pixels, returning a list of lines."""
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = " ".join(current + [word])
        if draw.textlength(test, font=font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines or [""]


def render_text(text):
    """Render text into a 250×122 1-bit PIL Image, word-wrapped and vertically centered."""
    img = Image.new("1", (DISPLAY_W, DISPLAY_H), 1)  # white background
    draw = ImageDraw.Draw(img)
    font = _load_font(18)

    padding = 10
    lines = _wrap_text(text, font, DISPLAY_W - 2 * padding, draw)

    _, top, _, bottom = font.getbbox("A")
    line_height = (bottom - top) + 6
    total_height = len(lines) * line_height
    y = (DISPLAY_H - total_height) // 2

    for line in lines:
        w = int(draw.textlength(line, font=font))
        x = (DISPLAY_W - w) // 2
        draw.text((x, y), line, font=font, fill=0)
        y += line_height

    return img


class EinkDisplay:
    def __init__(self):
        from waveshare_epd import epd2in13_V4
        self._epd = epd2in13_V4.EPD()

    def show(self, img: Image.Image):
        self._epd.init()
        self._epd.display(self._epd.getbuffer(img))
        self._epd.sleep()


class MockDisplay:
    PREVIEW_PATH = "display_preview.png"

    def show(self, img: Image.Image):
        preview = img.convert("L").resize(
            (DISPLAY_W * 2, DISPLAY_H * 2), Image.Resampling.NEAREST
        )
        preview.save(self.PREVIEW_PATH)
        print(f"[DISPLAY] saved preview → {self.PREVIEW_PATH}")
