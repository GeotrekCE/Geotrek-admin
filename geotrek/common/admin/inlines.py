from paperclip.admin import AttachmentInlines


class AttachmentInline(AttachmentInlines):
    extra = 0
    exclude = ("random_suffix",)
