from django.core.files.uploadedfile import SimpleUploadedFile

IMG_FILE = ''

def get_dummy_img():
    return IMG_FILE.decode('base64')

def get_dummy_uploaded_image(name='dummy_img.png'):
    return SimpleUploadedFile(name, get_dummy_img(), content_type='image/png')

# Alias
get_dummy_uploaded_file = get_dummy_uploaded_image
