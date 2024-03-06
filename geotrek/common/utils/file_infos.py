from chardet.universaldetector import UniversalDetector


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
