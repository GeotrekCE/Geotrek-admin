from django.templatetags.static import static
from tinymce.widgets import TinyMCE

FLATPAGE_TINYMCE_CONFIG = {
    "height": 500,
    "plugins": [
        'autolink',
        'lists',
        'link',
        'image',
        'media',
        'button-link',
        'table',
        'paste',
        'imagetools',
        'wordcount',
        'visualblocks',
        'code',
        'help',
    ],
    "menubar": False,
    'image_title': False,
    'image_caption': True,
    'automatic_uploads': True,
    'convert_urls': False,
    'file_picker_types': "image media",
    'images_upload_url': "/flatpages/tinymce/upload/",
    "toolbar": 'undo redo | styleselect | blockquote | bold italic forecolor |'
               'alignleft aligncenter alignright alignjustify | bullist numlist | link imagesGallery image media |'
               'button-link suggestions | removeformat visualblocks code | wordcount | help',
    "formats": {
        "informationFormat": {
            "block": 'div', "classes": 'information'
        }
    },
    "style_formats": [
        {"title": 'Headings', "items": [
            {"title": 'Headings 2', "format": 'h2'},
            {"title": 'Headings 3', "format": 'h3'},
            {"title": 'Headings 4', "format": 'h4'},
            {"title": 'Headings 5', "format": 'h5'},
            {"title": 'Headings 6', "format": 'h6'}
        ]},
        {"title": 'Inline', "items": [
            {"title": 'Bold', "format": 'bold'},
            {"title": 'Italic', "format": 'italic'},
            {"title": 'Underline', "format": 'underline'},
            {"title": 'Strikethrough', "format": 'strikethrough'},
        ]},
        {"title": 'Blocks', "items": [
            {"title": 'Paragraph', "format": 'p'},
            {"title": 'Blockquote', "format": 'blockquote'},
            {"title": 'Information', "format": 'informationFormat'},
        ]},
        {"title": 'Alignment', "items": [
            {"title": 'Left', "format": 'alignleft'},
            {"title": 'Center', "format": 'aligncenter'},
            {"title": 'Right', "format": 'alignright'},
            {"title": 'Justify', "format": 'alignjustify'}
        ]}
    ],
    "newline_behavior": '',
    "default_font_stack": ['-apple-system', 'Helvetica', 'Arial', 'sans-serif'],
    "theme": "silver",
    'paste_auto_cleanup_on_paste': True,
    'paste_as_text': True,
    "forced_root_block": "p",
    "width": "95%",
    "resize": "both",
    "browser_spellcheck": True,
    "contextmenu": False,
    'valid_elements': ('@[id|class|style|title|dir<ltr?rtl|lang|xml::lang],'
                       'a[rel|rev|charset|hreflang|tabindex|accesskey|type|name|href|target|title|class],'
                       'img[longdesc|usemap|src|border|alt=|title|hspace|vspace|width|height|align],'
                       'p,em/i,strong/b,div[align],br,ul,li,ol,span[style],'
                       'iframe[src|frameborder=0|alt|title|width|height|align|name],'
                       'h2,h3,h4,h5,h6,figure,figcaption,blockquote'),
    "setup": "tinyMceInit",
}


class FlatPageTinyMCE(TinyMCE):

    def __init__(self, *args, **kwargs):
        mce_attrs = FLATPAGE_TINYMCE_CONFIG.copy()
        mce_attrs["content_css"] = static("flatpages/tinymce/css/flatpage_custom_formats.css")
        kwargs["mce_attrs"] = mce_attrs
        super().__init__(*args, **kwargs)

    class Media:
        js = ('flatpages/tinymce/js/additional_tinymce_plugins.js',)
        css = {
             'all': ('flatpages/tinymce/css/flatpagetinymce_widget.css', )
        }
