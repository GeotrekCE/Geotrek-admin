from django.core.files.uploadedfile import SimpleUploadedFile

# Produce a small red dot
IMG_FILE = 'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='

def get_dummy_img():
    return IMG_FILE.decode('base64')

def get_dummy_uploaded_image(name='dummy_img.png'):
    return SimpleUploadedFile(name, get_dummy_img(), content_type='image/png')

def get_dummy_uploaded_file(name='dummy_file.txt'):
    return SimpleUploadedFile(name, 'HelloWorld', content_type='plain/text')
