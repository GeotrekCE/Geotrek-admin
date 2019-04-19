from PIL import ImageDraw
from PIL import ImageFont


def add_watermark(image, **kwargs):
    text = kwargs.get('text')
    size_watermark = kwargs.get('size_watermark')
    if not text:
        return image
    drawing = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size_watermark, encoding="unic")
    drawing.text((1, image.height - size_watermark - 1), text, 'black', font=font)
    drawing.text((0, image.height - size_watermark - 2), text, 'white', font=font)
    return image
