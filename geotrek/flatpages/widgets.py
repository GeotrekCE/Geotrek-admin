from django.templatetags.static import static
from tinymce.widgets import TinyMCE

FLATPAGE_TINYMCE_CONFIG = {
    "menubar": True,
    "content_style": '.left { text-align: left; }',
    "formats": {
        "alignleft": {
            "selector": 'p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table,img,audio,video',
            "classes": 'left'
        },
        "quote": {
            "inline": "span",
            "classes": "quote"
        },
        "bold": {
            "inline": 'span',
            "classes": 'bold'
        },
        "customformat": {
            "inline": 'span',
            "styles": {
                "color": '#00ff00',
                "fontSize": '20px'
            },
            "attributes": {
                "title": 'My custom format'
            },
            "classes": 'example1'
        }
    },
    "style_formats": [
        {"title": 'Custom format', "format": 'customformat'},
        {"title": 'Align left', "format": 'alignleft'},
        {"title": 'Bold text', "inline": 'strong'},
        {"title": 'Red header', "block": 'h1', "styles": {"color": '#ff0000'}},
        {"title": 'Badge', "inline": 'span',
         "styles": {"display": 'inline-block', "border": '1px solid #2276d2', 'border-radius': '5px',
                    "padding": '2px 5px', "margin": '0 2px', "color": '#2276d2'}},

        {"title": "quote", "inline": "span", "classes": "quote"},
        {"title": 'Image formats'},
        {"title": 'Image Left', "selector": 'img', "styles": {'float': 'left', 'margin': '0 10px 0 10px'}},
        {"title": 'Image Right', "selector": 'img', "styles": {'float': 'right', 'margin': '0 0 10px 10px'}},
    ]
}


class FlatPageTinyMCE(TinyMCE):

    def __init__(self, *args, **kwargs):
        mce_attrs = FLATPAGE_TINYMCE_CONFIG.copy()
        mce_attrs.update(kwargs.get("mce_attrs", {}))
        mce_attrs["content_css"] = static("flatpages/css/flatpage_custom_formats.css")
        kwargs["mce_attrs"] = mce_attrs
        super().__init__(*args, **kwargs)
