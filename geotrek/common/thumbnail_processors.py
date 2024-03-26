from PIL import ImageDraw, ImageFont


def add_watermark(image, **kwargs):
    text = kwargs.get('TEXT')
    size_watermark = kwargs.get('SIZE_WATERMARK')
    if not text:
        return image
    drawing = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size_watermark)
    drawing.text((1, image.height - size_watermark - 1), text, 'black', font=font)
    drawing.text((0, image.height - size_watermark - 2), text, 'white', font=font)
    return image
