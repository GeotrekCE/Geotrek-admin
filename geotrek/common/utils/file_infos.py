from chardet.universaldetector import UniversalDetector
import magic
from paperclip import is_an_image


def get_encoding_file(file_name):
    # Get encoding mode (utf-8, ascii, ISO-8859-1...)
    detector = UniversalDetector()
    detector.reset()
    for line in open(file_name, 'rb'):
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    return detector.result["encoding"]


def is_a_non_svg_image(filefield):
    file_mimetype = None
    if filefield:
        with filefield.open('rb') as file:
            file.seek(0)
            file_mimetype = magic.from_buffer(file.read(), mime=True)
    return is_an_image(file_mimetype) and file_mimetype.split('/')[1] == 'svg+xml'
