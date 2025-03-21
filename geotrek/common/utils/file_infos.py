from chardet.universaldetector import UniversalDetector
import magic


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
    if not file_mimetype:
        return False
    file_type, file_subtype = file_mimetype.split('/')
    return file_type == 'image' and file_subtype != 'svg+xml'
