from django.core.files.uploadedfile import SimpleUploadedFile

IMG_FILE = \
    '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'

def get_dummy_img():
    return IMG_FILE.decode('base64')

def get_dummy_uploaded_image(name='dummy_img.png'):
    return SimpleUploadedFile(name, get_dummy_img(), content_type='image/png')

# Alias
get_dummy_uploaded_file = get_dummy_uploaded_image


